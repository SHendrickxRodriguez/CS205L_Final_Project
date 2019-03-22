#Sebastian Hendrickx-Rodriguez
from abaqus import * #access to Abaqus objects and to a default model database mdb.
from abaqusConstants import * #to make the Symbolic Constants defined by Abaqus Scripting Interface available to the script
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import regionToolset
num = 33696


for t1 in range(0, 180, 5):
    for t2 in range(0, 180, 5):
        for t3 in range(0, 180, 5):
            #file = open("input.txt","a") 
            #file.write(str([t1,t2,t3]) + '\n')  
             
            #file.close() 
            #Open up a viewport of size 300x150 to see what you're doing lmao
            session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=300, 
                height=150)
            session.viewports['Viewport: 1'].makeCurrent()
            session.viewports['Viewport: 1'].maximize()

            ###MAKE MODEL
            ###
            #PART MODULE
            #Name SKETCH Model-1 and work on sheetSize of 400 units
            s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
                sheetSize=400.0)
            g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
            s.setPrimaryObject(option=STANDALONE)
            #Make a circle with center at origin and rightmost point at point1
            s.CircleByCenterPerimeter(center=(0, 0), point1=(20, 0))


            m = mdb.models['Model-1']
            #Create a new Part assigned to variable p
            p = m.Part(name='composite',dimensionality=THREE_D,
                                           type=DEFORMABLE_BODY)
            #Extrude your sketch as a shell a certain depth
            p.BaseShellExtrude(sketch=s, depth= 60)
            #Get the face of the cylinder and edges
            f1 = m.parts['composite'].faces
            s1 = m.parts['composite'].Surface(side1Faces=f1, name='Surf-1')
            e2 = m.parts['composite'].edges.findAt(((20.0, 0.0, 60.0), ), )
            s2 = m.parts['composite'].Set(edges=e2, name='Set-2')
            r1 = regionToolset.Region(faces=f1, edges=e2)
            #Look at what you did lol
            session.viewports['Viewport: 1'].setValues(displayedObject=p)

            #PROPERTY MODULE
            #What's your model made out of?
            m.Material(name='Rachis_Material', description='Keratin')
            #What are the properties of this orthrotopic material. Listed as
            #Engineering Constants: E1, E2, E3, Nu12, Nu13, Nu23, G12, G13, G23.
            m.materials['Rachis_Material'].Elastic(table=(
                (7, 7, 7, 0.3, 0.3, 0.3, 2.7, 2.7, 2.7), ), type=ENGINEERING_CONSTANTS)
            #m.materials['Rachis_Material'].Elastic(table=(
            #    (148000, 9200, 9200, 0.27, 0.27, 0.39, 5300, 5300, 2300), ), type=ENGINEERING_CONSTANTS)

            #Create Composite Layup
            compositeLayup = m.parts['composite'].CompositeLayup(
                name='Composite_Layup',
                description='Composite Layup of Rachis', elementType=SHELL,
                offsetType=MIDDLE_SURFACE)
            compositeLayup.Section(preIntegrate=OFF, integrationRule=SIMPSON,
                poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT,
                useDensity=OFF, nodalThicknessField='')
            compositeLayup.ReferenceOrientation(orientationType=DISCRETE, fieldName='',
                normalAxisDirection=AXIS_3, normalAxisDefinition=SURFACE, normalAxisRegion=s1,
                primaryAxisDirection=AXIS_1, primaryAxisDefinition=EDGE, primaryAxisRegion=s2)
            #Make layers with fibers at different angles=orientationvalue
            #Layers have thickness
            compositeLayup.CompositePly(suppressed=False, plyName='L1',
                region=r1, material='Rachis_Material', thicknessType=SPECIFY_THICKNESS,
                thickness=4, orientationType=SPECIFY_ORIENT,
                orientationValue=t1, numIntPoints=3)
            compositeLayup.CompositePly(suppressed=False, plyName='L2',
                region=r1, material='Rachis_Material', thicknessType=SPECIFY_THICKNESS,
                thickness=4, orientationType=SPECIFY_ORIENT,
                orientationValue=t2, numIntPoints=3)
            compositeLayup.CompositePly(suppressed=False, plyName='L3',
                region=r1, material='Rachis_Material', thicknessType=SPECIFY_THICKNESS,
                thickness=4, orientationType=SPECIFY_ORIENT,
                orientationValue=t3, numIntPoints=3)

            #ASSEMBLY MODULE
            # Create part instance
            #
            cAssembly = m.rootAssembly
            cAssembly.DatumCsysByDefault(CARTESIAN)
            cInstance = cAssembly.Instance(name='composite', part=p, dependent=ON)

            #STEP MODULE
            s = m.rootAssembly
            m.StaticStep(name='Step-1', previous='Initial',
                         description='Apply Loads')
            m.FieldOutputRequest(name='F-Output-2', 
                createStepName='Step-1', variables=('S', 'MISES', 'MISESMAX', 'E', 
                'U', 'UT', 'UR', 'RF'))

            #LOAD MODULE
            #Creation of the Boundary Conditions
            d = mdb.models['Model-1'].rootAssembly
            e_d = d.instances['composite'].edges
            region1 = d.Set(edges=e_d.findAt(((20.0, 0.0, 0.0), ), ), name='Set-1') #Bottom
            m.DisplacementBC(name='BC-1', createStepName='Step-1', 
                region=region1, u1=0, u2=0, u3=0, ur1=0, ur2=0, 
                ur3=0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, 
                fieldName='', localCsys=None)
            region2 = d.Set(edges=e_d.findAt(((20.0, 0.0, 60.0), ), ), name='Set-2') #Top
            m.DisplacementBC(name='BC-2', createStepName='Step-1', 
                region=region2, u1=0, u2=0, u3=UNSET, ur1=0, ur2=0, 
                ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, 
                fieldName='', localCsys=None)
            #m.ShellEdgeLoad(name='Load-1', createStepName='Step-1',
            #    region=region2, magnitude=0, distributionType=UNIFORM,
            #    traction=NORMAL)
            #region3 = d.edges.findAt(((15.0, 0.0, 100.0), ), )
            d.Surface(name='force_l_surf', side1Edges=d.instances['composite']
                .edges.getSequenceFromMask(('[#1]', ), ))
            m.ShellEdgeLoad(createStepName='Step-1',
                distributionType=UNIFORM, field='', follower=ON,
                localCsys=None, magnitude=-1, name='load_n',
                region=d.surfaces['force_l_surf'],
                traction=NORMAL)
            m.ShellEdgeLoad(createStepName='Step-1',
                distributionType=UNIFORM, field='', follower=ON,
                localCsys=None, magnitude=1, name='load_s',
                region=d.surfaces['force_l_surf'],
                traction=SHEAR)


            #MESH MODULE
            ps = m.parts['composite']
            ps.seedPart(size=2.8, deviationFactor=0.1, minSizeFactor=0.1)
            ps.generateMesh()

            #JOB MODULE
            J1 = mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, 
                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
                scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
            J1.submit()
            J1.waitForCompletion()

            #Post Processing
            o1 = session.openOdb(name='Job-1.odb')
            odb = session.odbs['Job-1.odb']
            frames = o1.steps['Step-1'].frames
            numFrames = len(frames)
            #I = o1.rootAssembly.instances['composite']
            #numNodes = len(I.nodes)
            #numElements = len(myInstance.elements)
            S = odb.steps['Step-1'].frames[1].fieldOutputs['S'].getSubset(
                position=ELEMENT_NODAL)
            E = odb.steps['Step-1'].frames[1].fieldOutputs['E'].getSubset(
                position=ELEMENT_NODAL)
            S1 = []
            E1 = []
            for k in range(0, 8*945 - 1, 1889):
                S1.append(S.getScalarField(invariant=MISES).values[k].data)
                E1.append(E.getScalarField(invariant=MAX_PRINCIPAL).values[k].data)



            #file = open("output.txt","a") 
            #file.write(str(S1) + '\n')
            #file.write(str(E1) + '\n')
             
            #file.close()
            print(num)
            num = num + 1;
            #for el in range(0,numElements):
            #    Stress = o1.steps['Step-1'].frames[fr].fieldOutpus['S'].getSubset(
            #        region=I.elements[el], poisition=CENTROID,
            #        elementType='C3D8H').values
            #    sz = len(Stress)
            #    for ip in range(0,sz):
            #        Sxx = Stress[ip].data[0]
            #        Syy = Stress[ip].data[1]
            #        Szz = Stress[ip].data[2]
            #        Sxy = Stress[ip].data[3]
            #        Sxz = Stress[ip].data[4]
            #        Syz = Stress[ip].data[5]
            #session.writeFieldReport(
            #    fileName='Output.txt',
            #    append=OFF, sortItem='Node Label', odb=odb, step=1, frame=0,
            #    outputPosition=NODAL, variable=(('S', INTEGRATION_POINT, ((INVARIANT,'Mises'), )), ))
