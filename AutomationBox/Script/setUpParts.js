var fullPath = GetCurrentDirectory();
var jsonPath = fullPath+'\\config.json';
var settingFile = new File(jsonPath, File.READ);
var data=JSON.parse(settingFile.ReadAll());
var caseToRun=data.caseToRun;

//var m = new Model(1);
var m = Model.GetFromID(1);

var numberOfSources=data[caseToRun].LidNGate.numberOfSources;
var soilParameters=data[caseToRun].SoilParameters

function setUpMaterialProperties()
{
	const materialArray = new Array();

	var a2=Math.sin(soilParameters.InternalFrictionAngle * (Math.PI / 180)) ** 2
	var a1=2 * soilParameters.cohesion * Math.sin(soilParameters.InternalFrictionAngle * (Math.PI / 180)) * Math.cos(soilParameters.InternalFrictionAngle * (Math.PI / 180));
	var a0=(soilParameters.cohesion * Math.cos(soilParameters.InternalFrictionAngle * (Math.PI / 180))) ** 2

	materialArray.push(new Material(m, 1, "RIGID"));
	materialArray[0].SetPropertyByName("RO", 1900);
	materialArray[0].SetPropertyByName("E", 100000000.0);
	materialArray[0].SetPropertyByName("PR", 0.3);
	materialArray[0].SetPropertyByName("CMO", 1.0);
	materialArray[0].SetPropertyByName("CON1", 7.0);
	materialArray[0].SetPropertyByName("CON2", 7.0);

	materialArray.push(new Material(m, 2, "RIGID"));
	materialArray[1].SetPropertyByName("RO", 2500);
	materialArray[1].SetPropertyByName("E", 100000000.0);
	materialArray[1].SetPropertyByName("PR", 0.3);
	materialArray[1].SetPropertyByName("CMO", 1.0);
	materialArray[1].SetPropertyByName("CON1", 4.0);
	materialArray[1].SetPropertyByName("CON2", 7.0);

	materialArray.push(new Material(m, 3, "SOIL_AND_FOAM"));
	materialArray[2].SetPropertyByName("RO", 1900);
	materialArray[2].SetPropertyByName("G", 6000000.0);
	materialArray[2].SetPropertyByName("KUN", 12000000.0);
	materialArray[2].SetPropertyByName("A0", a0);
	materialArray[2].SetPropertyByName("A1", a1);
	materialArray[2].SetPropertyByName("A2", a2);
	materialArray[2].SetPropertyByName("PC", -1e8);
	materialArray[2].SetPropertyByName("VCR", 1.0);
	materialArray[2].SetPropertyByName("P2", 12000000.0);

	materialArray.push(new Material(m, 4, "VACUUM"));
	materialArray[3].SetPropertyByName("RHO", 1.28);
	
	return materialArray;
}

function setUpSectionProperties()
{
	const sectionArray = new Array();
		
	sectionArray.push(new Section(m, 1, Section.SHELL, 'Topography'));
	sectionArray[0].elform = 2;
	sectionArray[0].t1     = 0.1;
	sectionArray[0].t2     = 0.1;
	sectionArray[0].t3     = 0.1;
	sectionArray[0].t4     = 0.1;
	
	sectionArray.push(new Section(m, 2, Section.SOLID, 'Debris'));
	sectionArray[1].elform = 11;
	
	return sectionArray;
}

function setUpPartProperties(numberOfSources)
{
	const partArray     = new Array();
	partArray.push(new Part(m, 1, 1, 1, 'Topography'));
	partArray.push(new Part(m, 4, 2, 3, 'Debris'));
	partArray.push(new Part(m, 5, 2, 4, 'Air'));
	
	for (var aa = 0; aa < numberOfSources; aa++)
	{
		partNumber = 11 + aa * 2;
		partArray.push(new Part(m, partNumber,     1, 2, 'Gate #' + String(aa + 1)));
		partArray.push(new Part(m, partNumber + 1, 1, 2, 'Lid #' + String(aa + 1)));
	}
	
	for (var bb = 0; bb < partArray.length; bb++)
	{
		partArray[bb].hgid = 1;
	}
}

function setUpCurves()
{
	const curveArray     = new Array();
	curveArray.push(new Curve(Curve.CURVE, m, 1));
	curveArray[0].AddPoint(  0.0,    0.0);
	curveArray[0].AddPoint(  2.0,    0.0);
	curveArray[0].AddPoint(  2.01, 100.0);
	curveArray[0].AddPoint(100.0,  100.0);

	curveArray.push(new Curve(Curve.CURVE, m, 2));
	curveArray[1].AddPoint(  0.0, 0.0);
	curveArray[1].AddPoint(  2.0, 1.0);
	curveArray[1].AddPoint(100.0, 1.0);
	curveArray[1].AddPoint(300.0, 1.0);
	
	return curveArray;
}

function setUpPrescribedMotion(numberOfSources)
{
	const PrescribedMotionArray = new Array();
	for (var aa = 0; aa < numberOfSources; aa++)
	{
		partNumber = 11 + aa * 2;
		
		PrescribedMotionArray.push(new PrescribedMotion(m, partNumber, 
			3, 2, 1, PrescribedMotion.RIGID));
		PrescribedMotionArray.push(new PrescribedMotion(m, partNumber + 1, 
			3, 2, 1, PrescribedMotion.RIGID));
	}
}

function setUpHourglass()
{
	var hourglass = new Hourglass(m, 1);
	hourglass.qm  = 1.0e-8;
	
	return hourglass
}	

function setUpControl()
{
	m.control.ale.exists = true;
	m.control.ale.dct    = -1;
	m.control.ale.nadv   = 1;
	m.control.ale.meth   = 1;
	m.control.ale.afac   = -1.0;

	m.control.mpp_decomposition_distribute_ale_elements.exists  = true;
	m.control.mpp_decomposition_distribute_ale_elements.overlap = 0;

	m.control.output.exists  = true;
	m.control.output.npopt   = 1;
	m.control.output.neecho  = 3;

	m.control.termination.exists = true;
	m.control.termination.endtim = 100;

	m.control.timestep.exists = true;
	m.control.timestep.tssfac = 0.5;
}

function setUpDatabase()
{
	m.database.glstat.exists = true;
	m.database.glstat.dt     = 0.15;
	m.database.glstat.bin    = 1;

	m.database.binary.d3plot.exists = true;
	m.database.binary.d3plot.dt     = 0.5;

	m.database.extent_binary.exists = true;
	m.database.extent_binary.ieverp = 1;
}

function setUpSPCs()
{
	var b = new Spc(m, 1, 0, 1, 1, 0, 0, 0, 0, Spc.SET)
}

function setUpSets()
{
	const setArray     = new Array();
	setArray.push(new Set(m, 2, Set.PART));
	setArray[0].Add(4);
	setArray[0].Add(5);
	
	for (var aa = 0; aa < 2; aa++)
	{
		setArray.push(new Set(m, aa + 3, Set.PART));
		var partNumber = 11 + aa;
		for (var bb = 0; bb < numberOfSources; bb++)
		{
			setArray[aa + 1].Add(partNumber + bb);
		}

	}
}

materialArray = setUpMaterialProperties();
sectionArray  = setUpSectionProperties();
partArray     = setUpPartProperties(numberOfSources);
hourglass     = setUpHourglass();
setUpControl();
setUpDatabase();
setUpCurves();
setUpPrescribedMotion(numberOfSources);
//setUpSPCs();
setUpSets();

function formatNumber(num,dp) {
    // Format the number to 5 decimal places
    let formattedNum = num.toFixed(dp);
    // Pad the number with spaces to ensure it is 8 characters long
    return formattedNum.padStart(8, ' ');
}

var relDamping     = "       0.0       1.0         1         2"+formatNumber(soilParameters.DV2,2)+"         0"
var databaseALEMat = "       0.1         0         0"
var loadBodyZ      = "         2       9.8         0"
var aleMultiMaterialGroup = 
					 "         5         1" + "\n" + 
					 "         4         1"
var initVolFracGeom = 
					 "         4         1         1         0" + "\n" + 
					 "         1         0         2       0.0       0.0       0.0" + "\n" + 
					 "         1         1         0       0.0" + "\n" + 
					 "         1         1         1       0.0       0.0       0.0" + "\n" + 
					 "         3         0         0       0.0" + "\n" + 
					 "         1         1         1       0.0       0.0       0.0" + "\n" + 
					 "         4         0         0       0.0"

var essentialBoundary = "         4         1         1         0"

const constrLagrangeInSolidArray     = new Array();
var b=Math.tan(soilParameters.BasalFrictionAngle * (Math.PI / 180))
Message(b)



constrLagrangeInSolidArray.push(
	"         1Debris on Topo                                                        " + "\n" +
	"         1         4         1         1         0         4         2         1" + "\n" + 
	"       0.0       0.0       0.0"+formatNumber(b,5)+"      0.1         0         1       0.0" + "\n" + 
	"       0.0       0.0       0.0         1       0.0         0         0         0" + "\n" + 
	"         0         0         0         0       0.0         0       0.0" + "\n" + 
	"       0.0       0.0       0.0       0.0       0.0       0.0                 0.0"
	)

constrLagrangeInSolidArray.push(
"         2Debris on Gate                                                        " + "\n" +
"         3         4         0         1         0         4         2         1" + "\n" +
"       0.0       0.0       0.0      0.01      0.01         0         1       0.0" + "\n" +
"       0.0       0.0       0.0         1       0.0         0         0         0" + "\n" +
"         0         0         0         0       0.0         0       0.0" + "\n" +
"       0.0       0.0       0.0       0.0       0.0       0.0                 0.0"
)
constrLagrangeInSolidArray.push(
"         3Debris on Lid                                                         " + "\n" +
"         4         4         0         1         0         4         2         1" + "\n" +
"       0.0       0.0       0.0      0.01      0.01         0         1       0.0" + "\n" +
"       0.0       0.0       0.0         1       0.0         0         0         0" + "\n" +
"         0         0         0         0       0.0         0       0.0" + "\n" +
"       0.0       0.0       0.0       0.0       0.0       0.0                 0.0"
)



f = new File("./ibtmp.key", File.WRITE);
 
f.Write("*DAMPING_RELATIVE\n");
f.Write(relDamping);
f.Write("\n");

f.Write("*DATABASE_ALE_MAT\n");
f.Write(databaseALEMat);
f.Write("\n");

f.Write("*ALE_MULTI-MATERIAL_GROUP\n");
f.Write(aleMultiMaterialGroup);
f.Write("\n");

f.Write("*ALE_ESSENTIAL_BOUNDARY\n");
f.Write(essentialBoundary);
f.Write("\n");

f.Write("*LOAD_BODY_Z\n");
f.Write(loadBodyZ);
f.Write("\n");

f.Write("*INITIAL_VOLUME_FRACTION_GEOMETRY\n");
f.Write(initVolFracGeom);
f.Write("\n");

for (var aa = 0; aa < 3; aa++)
{
	f.Write("*CONSTRAINED_LAGRANGE_IN_SOLID_TITLE\n");
	f.Write(constrLagrangeInSolidArray[aa]);
	f.Write("\n");
}

f.Write("*END\n");
f.Close();
 
m.Import("ibtmp.key"); // merge temp file back into main model
 
var deleted = File.Delete("ibtmp.key") // delete temp file

f = new File("./MikeTest.key", File.WRITE);
f.Write("\n");
f.Close();

