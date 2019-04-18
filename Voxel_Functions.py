# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 11:47:11 2019

@author: WilmesD
"""
from math import sqrt,sin,cos,pow,exp,asin,atan2,pi
from direct.showbase.ShowBase import ShowBase
import panda3d.core as pd
import numpy as np

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
    node = pd.GeomNode("gnode")
    node.addGeom(geom)
    return node

def addStitchVertices(vertexd,current_vertices,x1_vertices,x,y,z,addx,addy,addz,subx,suby,subz,faces,colord,texcoordd,f,vdata,stepsize):
                                
    vertexd.add_data3f((x1_vertices[(x,y,z)][0],x1_vertices[(x,y,z)][1],x1_vertices[(x,y,z)][2]))
#    h = x1_vertices[(x,y,z)][2]
    colord.add_data4f(stepsize/2,0,0,1)
    texcoordd.add_data2f(0,1)
        
    vertexd.add_data3f((current_vertices[(x+subx,y+suby,z+subz)][0],current_vertices[(x+subx,y+suby,z+subz)][1],current_vertices[(x+subx,y+suby,z+subz)][2]))
#    h = current_vertices[(x+subx,y+suby,z+subz)][2]
    colord.add_data4f(stepsize/2,0,0,1)
    texcoordd.add_data2f(0,0)
    
    vertexd.add_data3f((x1_vertices[(x+addx,y+addy,z+addz)][0],x1_vertices[(x+addx,y+addy,z+addz)][1],x1_vertices[(x+addx,y+addy,z+addz)][2]))
#    h = x1_vertices[(x+addx,y+addy,z+addz)][2]
    colord.add_data4f(stepsize/2,0,0,1)
    texcoordd.add_data2f(1,1)
    
    vertexd.add_data3f((current_vertices[(x+addx+subx,y+addy+suby,z+addz+subz)][0],current_vertices[(x+addx+subx,y+addy+suby,z+addz+subz)][1],current_vertices[(x+addx+subx,y+addy+suby,z+addz+subz)][2]))
#    h = current_vertices[(x+addx+subx,y+addy+suby,z+addz+subz)][2]
    colord.add_data4f(stepsize/2,0,0,1)
    texcoordd.add_data2f(1,0)

def StitchLoop(f,all_vertices,vdata,difx,dify,difz,dist,stepsize):
    faces = []
    vertexd = pd.GeomVertexWriter(vdata, "vertex")
    colord = pd.GeomVertexWriter(vdata, "color")
    texcoordd = pd.GeomVertexWriter(vdata, "texcoord")
    
    for x in range(-1*difx,2*difx,difx):
        for yi in range(-1*dify,2*dify,1):
            for zi in range(-1*difz,2*difz,1):
                
                if (x-1,yi,zi) in all_vertices and (x,yi,zi) in all_vertices:
                    if (x-1,yi+1,zi) in all_vertices and (x,yi+1,zi) in all_vertices:
                        
                        addStitchVertices(vertexd,all_vertices,all_vertices,x,yi,zi,0,1,0, -1,0,0, faces, colord, texcoordd,f,vdata,stepsize)
#                        print("Vertices Added")
                        checkside = f(x,yi+1,zi+1) < 0
                        numV = vertexd.getWriteRow()
                        faces.append(make_face(numV-4,numV-3,numV-1,numV-2,checkside,vdata))
                        
                    if (x-1,yi,zi+1) in all_vertices and (x,yi,zi+1) in all_vertices:
                        
                        addStitchVertices(vertexd,all_vertices,all_vertices,x,yi,zi,0,0,1, -1,0,0, faces, colord, texcoordd,f,vdata,stepsize)
#                        print("Vertices Added")
                        checkside1 = f(x,yi+1,zi+1) > 0
                        numV = vertexd.getWriteRow()
                        faces.append(make_face(numV-4,numV-3,numV-1,numV-2,checkside1,vdata))
#                    
    for y in range((-1)*dify,2*dify,dify):
        for xi in range((-1)*difx,2*difx,1):
            for zi in range((-1)*difz,2*difz,1):
                if (xi,y-1,zi) in all_vertices and (xi,y,zi) in all_vertices:
                    
                    if ((xi+1,y-1,zi) in all_vertices and (xi+1,y,zi) in all_vertices):
                        
                        addStitchVertices(vertexd,all_vertices,all_vertices,xi,y,zi,1,0,0, 0,-1,0, faces, colord, texcoordd,f,vdata,stepsize)
#                        print("Vertices Added")
                        checkside = f(xi+1,y,zi+1) > 0
                        numV = vertexd.getWriteRow()
                        faces.append(make_face(numV-4,numV-3,numV-1,numV-2,checkside,vdata))
                        
                    if ((xi,y-1,zi+1) in all_vertices and (xi,y,zi+1) in all_vertices):
                        
                        addStitchVertices(vertexd,all_vertices,all_vertices,xi,y,zi,0,0,1, 0,-1,0, faces, colord, texcoordd,f,vdata,stepsize)
#                        print("Vertices Added")
                        checkside = f(xi+1,y,zi+1) < 0
                        numV = vertexd.getWriteRow()
                        faces.append(make_face(numV-4,numV-3,numV-1,numV-2,checkside,vdata))
                    
    for z in range((-1)*difz,2*difz,difz):
        for xi in range((-1)*difx,2*difx,1):
            for yi in range((-1)*dify,2*dify,1):
                if (xi,yi,z-1) in all_vertices and (xi,yi,z) in all_vertices:
                    
                    if ((xi+1,yi,z-1) in all_vertices and (xi+1,yi,z) in all_vertices):
                        
                        addStitchVertices(vertexd,all_vertices,all_vertices,xi,yi,z,1,0,0, 0,0,-1, faces, colord, texcoordd,f,vdata,stepsize)
#                        print("Vertices Added")
                        checkside = f(xi+1,yi+1,z) < 0
                        numV = vertexd.getWriteRow()
                        faces.append(make_face(numV-4,numV-3,numV-1,numV-2,checkside,vdata))
#                        
                    if ((xi,yi+1,z-1) in all_vertices and (xi,yi+1,z) in all_vertices):
                        
                        addStitchVertices(vertexd,all_vertices,all_vertices,xi,yi,z,0,1,0, 0,0,-1, faces, colord, texcoordd,f,vdata,stepsize)
#                        print("Vertices Added")
                        checkside = f(xi+1,yi+1,z) > 0
                        numV = vertexd.getWriteRow()
                        faces.append(make_face(numV-4,numV-3,numV-1,numV-2,checkside,vdata))  
                        
    
#    for x in range((-dist+1)*difx,2*difx,difx):
#        for yi in range((-dist+1)*dify,2*dify,1):
#            for zi in range((-dist+1)*difz,2*difz,1):
#                if x/difx > -1 and x/difx < 2:
#                    continue
                
                
    
    return faces