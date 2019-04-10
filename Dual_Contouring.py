# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 08:21:14 2019

@author: WilmesD
"""
from math import sqrt,sin,cos,pow,exp,asin,atan2
from direct.showbase.ShowBase import ShowBase
import panda3d.core as pd
import numpy as np

dims = 10
xmin = -dims
xmax = dims
ymin = -dims
ymax = dims
zmin = -dims
zmax = dims

def ball(x,y,z):
    a = 4 - sqrt(pow(x,2)+pow(y,2)+pow(z,2))
    return a

def terrain(x,y,z):
    if z < sin(x):
        return 1
    else:
        return -1

def line(x,y,z):
    if abs(y) < 1:
        if abs(z-x) < 1:
            return 1
        else:
            return -1
    else:
        return -1

def makeGradients(f,x,y,z):
    c = 0.01
    return ((f(x+c,y,z)-f(x-c,y,z))/(2*c),
            (f(x,y+c,z)-f(x,y-c,z))/(2*c),
            (f(x,y,z+c)-f(x,y,z-c))/(2*c))

def interpolate_sign_change(v1,v2):
    return (0-v1)/(v2-v1)

def solve_lstsqrs_cost_function(positions,normals):
    A = np.array(normals)
    b = [v[0] * n[0] + v[1] * n[1] + v[2] * n[2] for v, n in zip(positions, normals)]
    s,_,_,_ = np.linalg.lstsq(A,b,0.05)
    return s
    
def make_face(v1,v2,v3,v4,cw,vdata):
    prim = pd.GeomTristrips(pd.Geom.UHStatic)
    if cw != True:
        prim.addVertices(v2,v3,v1,v4)
    else:
        prim.addVertices(v2,v1,v3,v4)
        
    prim.close_primitive()
    return prim
    

def make_mesh(vdata,faces):
    geom = pd.Geom(vdata)
    for prim in faces:    
        geom.add_primitive(prim)
    node = pd.GeomNode('gnode')
    node.addGeom(geom)
    return node
    

def find_vertex_in_voxel(f,x,y,z):
    #Look for sign change
    v = np.empty((2,2,2))
    for dx in (0,1):
        for dy in (0,1):
            for dz in (0,1):
                v[dx,dy,dz] = f(x+dx,y+dy,z+dz)
                
    #save exact points of sign changes in list
    change = []
    for dx in (0, 1):
        for dy in (0, 1):
            if (v[dx, dy, 0] > 0) != (v[dx, dy, 1] > 0):
                change.append((x+dx,y+dy,z+interpolate_sign_change(v[dx, dy, 0],v[dx, dy, 1])))
                
    for dx in (0, 1):
        for dz in (0, 1):
            if (v[dx, 0, dz] > 0) != (v[dx, 1, dz] > 0):
                change.append((x+dx,y+interpolate_sign_change(v[dx, 0, dz],v[dx, 1, dz]),z+dz))
                
    for dy in (0, 1):
        for dz in (0, 1):
            if (v[0, dy, dz] > 0) != (v[1, dy, dz] > 0):
                change.append((x+interpolate_sign_change(v[0, dy, dz],v[1, dy, dz]),y+dy,z+dz))
                
    if len(change) <= 1:
        return None
    #print(len(change))
    #get normals from gradients (actually gradients == normals)
    normals = []
    for v in change:
        n = makeGradients(f,v[0],v[1],v[2])
        normals.append([n[0],n[1],n[2]])
        
    #add bias to cost function to reduce likelyhood that the resulting point lies outside the voxel-boundary
    change.append(np.mean(change,axis=0))
    normals.append([0.5,0,0])
    change.append(np.mean(change,axis=0))
    normals.append([0,0.5,0])
    change.append(np.mean(change,axis=0))
    normals.append([0,0,0.5])
        
    #Solve Least Squares cost function 
    #sum( dot(p-v[i], n[i])^2 ) with p = point, v[i] = sign-change-positions, n[i] = normals
    #Basically "Find the point that is as orthogonal to the normals as possible and minimizes the distance to the sign-change-points"
    s = solve_lstsqrs_cost_function(change, normals)
    return s
    

def dual_contouring(f,xmin,xmax,ymin,ymax,zmin,zmax,vdata):
    vert_array = []
    vert_indices = {}
    vertexd = pd.GeomVertexWriter(vdata, 'vertex')
    colord = pd.GeomVertexWriter(vdata, 'color')
    texcoordd = pd.GeomVertexWriter(vdata, 'texcoord')
    for x in range(xmin,xmax):
        for y in range(ymin,ymax):
            for z in range(zmin,zmax):
                vert = find_vertex_in_voxel(f,x,y,z)
                if vert is None:
                    continue
                vertexd.add_data3f(vert[0],vert[1],vert[2])
                if vertexd.getWriteRow() % 4 == 0:
                    colord.add_data4f(1,1,1,1)
                    texcoordd.add_data2f(0,0)
                elif vertexd.getWriteRow() % 3 == 0:
                    colord.add_data4f(0,0,1,1)
                    texcoordd.add_data2f(0,1)
                elif vertexd.getWriteRow() % 2 == 0:
                    colord.add_data4f(0,1,0,1)
                    texcoordd.add_data2f(1,1)
                else:
                    colord.add_data4f(1,0,0,1)
                    texcoordd.add_data2f(1,0)
                    
                vert_indices[(x,y,z)] = len(vert_array)
                vert_array.append(vert)
    print("Num Vertices:")
    print(vertexd.getWriteRow())
    faces = []
    for x in range(xmin,xmax):
        for y in range(ymin,ymax):
            for z in range(zmin,zmax):
                if x > xmin and y > ymin:
                    inside1 = f(x,y,z) > 0
                    inside2 = f(x,y,z+1) > 0
                    if inside1 != inside2:
                        faces.append(make_face(vert_indices[(x-1,y-1,z)],
                                               vert_indices[(x-0,y-1,z)],
                                               vert_indices[(x-0,y-0,z)],
                                               vert_indices[(x-1,y-0,z)],inside2,vdata))
                if x > xmin and z > zmin:
                    inside1 = f(x,y,z) > 0
                    inside2 = f(x,y+1,z) > 0
                    if inside1 != inside2:
                        faces.append(make_face(vert_indices[(x-1,y,z-1)],
                                               vert_indices[(x-0,y,z-1)],
                                               vert_indices[(x-0,y,z-0)],
                                               vert_indices[(x-1,y,z-0)],inside1,vdata))
                if y > ymin and z > zmin:
                    inside1 = f(x,y,z) > 0
                    inside2 = f(x+1,y,z) > 0
                    if inside1 != inside2:
                        faces.append(make_face(vert_indices[(x,y-1,z-1)],
                                               vert_indices[(x,y-0,z-1)],
                                               vert_indices[(x,y-0,z-0)],
                                               vert_indices[(x,y-1,z-0)],inside2,vdata))
    print("Num Faces:")
    print(len(faces))
    return faces
            

class myapp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        gformat = pd.GeomVertexFormat.getV3cpt2()
        vdata = pd.GeomVertexData('Triangle', gformat, pd.Geom.UHStatic)
        vdata.setNumRows(2000)
        
        #Enter your function as the first argument here
        faces = dual_contouring(line,xmin,xmax,ymin,ymax,zmin,zmax,vdata)
        node = make_mesh(vdata, faces)
        self.render.attachNewNode(node)


app = myapp()
app.run()




