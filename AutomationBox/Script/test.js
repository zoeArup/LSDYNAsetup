var fullPath = GetCurrentDirectory();
var jsonPath = fullPath+'\\config.json';
// Message(jsonPath)
var settingFile = new File(jsonPath, File.READ)
var data=JSON.parse(settingFile.ReadAll())
settingFile.Close();
var caseToRun=data.caseToRun
var soilParameters=data[caseToRun].SoilParameters
var b=Math.tan(soilParameters.BasalFrictionAngle * (Math.PI / 180))
var a2=Math.sin(soilParameters.InternalFrictionAngle * (Math.PI / 180)) ** 2
var a1=2 * soilParameters.cohesion * Math.sin(soilParameters.InternalFrictionAngle * (Math.PI / 180)) * Math.cos(soilParameters.InternalFrictionAngle * (Math.PI / 180));
var a0=(soilParameters.cohesion * Math.cos(soilParameters.InternalFrictionAngle * (Math.PI / 180))) ** 2
Message(a0)
Message(a1)
Message(a2)

// function readJSONFile(filePath) {
// 	fetch(filePath)
//     .then((response) => response.json())
//     .then((json) => Message(json.caseToRun));
// }
// readJSONFile(fullPath);
