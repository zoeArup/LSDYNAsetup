// memory: 5000

//////////////////////////////////////////////////////////////////////////
//                                                                      //
//                                            Script by Saoirse Goodwin //
//                                                                      //
// - Updated 8th January 2024                                           //
//                                                                      //
// - Generates a box-shaped container & lid, as well as the debris.     //
//                                                                      //
// - You still need to manually trim down the debris to fit, and add    //
//   the SPCs for it.                                                   //
//                                                                      //
// - Also, check the default settings in the model.                     //
//                                                                      //
// - The script works on arbitrary resolutions. The resolution is taken //
//   from the model title.                                              //
//                                                                      //
//////////////////////////////////////////////////////////////////////////

var m = Model.GetFromID(1);

////////////////////////////////////////////////////////////////////
// MAIN SETTINGS 
////////////////////////////////////////////////////////////////////

var fullPath = GetCurrentDirectory();
var jsonPath = fullPath+'\\config.json';
var settingFile = new File(jsonPath, File.READ);
var data=JSON.parse(settingFile.ReadAll());
var caseToRun=data.caseToRun;
var LidNGate=data[caseToRun].LidNGate;

var  volume = LidNGate.VolumeSource;
const boxSize = LidNGate.boxSize;
const centreCoords = LidNGate.SourceCentreCoords;
var numberOfSources=LidNGate.numberOfSources;

////////////////////////////////////////////////////////////////////
// SECONDARY SETTINGS
////////////////////////////////////////////////////////////////////
var title    = m.title;
var gridSize = Number(title.replace(/[^0-9\.]+/g,""));

var solidStarting  = -gridSize * 1;
var solidDepth     = LidNGate.ALESoildHeight;
var gateMeshHeight = gridSize / 2;
var edgeThreshold  = gridSize * 0.8;

////////////////////////////////////////////////////////////////////
// FUNCTIONS
////////////////////////////////////////////////////////////////////
function getBoundingCoords(centreCoordsOneDim, boxSizeOneDim)
{
	const coords = [centreCoordsOneDim - boxSizeOneDim / 2,
					centreCoordsOneDim + boxSizeOneDim / 2];

	return coords
}


function getCurrentNumberOfNodes()
{
	/*Message("can get into getcurrentnumber of nodes");

	Message("can get node ");
	Message(Node);*/

	//Message("can get m ");
	//Message(m);

	var allNodes = Node.GetAll(m);
	
	/*Message("can get into all nodes");

	Message(allNodes.toString());*/

	var numberOfNodes = allNodes.length

	/*Message("can get into numberofnodes");

	Message(numberOfNodes.toString());*/

	return numberOfNodes;
}

function getCurrentNumberOfShells()
{
	var allShells = Shell.GetAll(m);
	var numberOfShells = allShells.length
	return numberOfShells;
}

function getBoxBounds(coords)
{
	Message("Getting BoxBound");
	function getMinimumCoords(currentMin, coord)
	{
		if (currentMin > coord)
		{
			currentMin = coord;
		}
		return currentMin;
	}

	function getMaximumCoords(currentMax, coord)
	{
		if (currentMax < coord)
		{
			currentMax = coord;
		}
		return currentMax;
	}
	
	const minCoords = [1e8, 1e8]; // Arbitrarily large.
	const maxCoords = [0, 0];
	
	var numberOfNodes  = coords.length;
	
	for (var aa = 0; aa < numberOfNodes; aa++)
	{
		minCoords[0] = getMinimumCoords(minCoords[0], coords[aa][0]);
		minCoords[1] = getMinimumCoords(minCoords[1], coords[aa][1]);
		maxCoords[0] = getMaximumCoords(maxCoords[0], coords[aa][0]);
		maxCoords[1] = getMaximumCoords(maxCoords[1], coords[aa][1]);
	}
	
	var noOfNodes_X = 0; 	
	var noOfNodes_Y = 0;

	for (var aa = 0; aa < numberOfNodes; aa++)
	{
		if ( (Math.abs(minCoords[0] - coords[aa][0])) < 0.000001) 
		{
			noOfNodes_X += 1;
		}
		if ( (Math.abs(minCoords[1] - coords[aa][1])) < 0.000001)
		{
			noOfNodes_Y += 1;
		}
	}	
	
	const noOfBoxNodes = [noOfNodes_X, noOfNodes_Y];
	
	return noOfBoxNodes;
}

function copyNodesForSolids(nodeArray, debrisHeight)
{
	//Message("Copying nodes for solids");
	var numberOfNodes        = nodeArray.length;

	//Message("Node array length");
	//Message(numberOfNodes);
	
	var numberOfLayers       = ((debrisHeight - solidStarting) / solidDepth) + 6;
	var counter              = 0;
	const solidNodeIDs       = new Array();

	for (var bb = 0; bb < numberOfLayers; bb++)
	{	
		for (var aa = 0; aa < numberOfNodes; aa++)
		{
			solidNodeIDs.push([nodeArray[aa][0], nodeArray[aa][1], nodeArray[aa][2], numberOfNodes + counter + 1]);

			var newNode = new Node(m,
				numberOfNodes + counter + 1, 
				nodeArray[aa][0], 
				nodeArray[aa][1],
				nodeArray[aa][2] + solidStarting + bb * solidDepth);
			
			//Message(" solidNodeIds"+solidNodeIDs.toString());

			counter += 1;
			
		}

		//Message(" solidNodeIds"+solidNodeIDs.toString());

	}

	return solidNodeIDs;

}



function makeSolids(counter, shellIDIncrement, solidNodes, partNumber)
{
	var s = new Solid(m, counter + shellIDIncrement + 1, partNumber, 
				solidNodes[0], solidNodes[1], solidNodes[2], solidNodes[3],
				solidNodes[4], solidNodes[5], solidNodes[6], solidNodes[7]
			);
	
	if (counter % 2000 === 0) {

		Message("Printing s");
		Message(s);
		Message("solid nodes?");
		Message(solidNodes[0]);
		Message(solidNodes[1]);
		Message(solidNodes[2]);
		Message(solidNodes[3]);
		Message(solidNodes[4]);
		Message(solidNodes[5]);
		Message(solidNodes[6]);
		Message(solidNodes[7]);
		Message(solidNodes[8]);

	}

}

function createSolids(solidNodeIDs, fullDomainNoOfNodes)
{
	Message("creating solids");
	//fulldomainnofnodes just to get counter
	//node id get 8 set --> makesolid
	//solidnodeID --> csv
	//fulldomainofnodes no need because already know solid node id len

	function getSolidCoordinates()
	{
		const solidNodes = [
			solidNodeIDs[0 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][3], // why per column tho
			solidNodeIDs[1 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][3],
			solidNodeIDs[1 + aa + ((bb + 1) * nodesPerColumn) + (cc * nodesPerLayer)][3],
			solidNodeIDs[0 + aa + ((bb + 1) * nodesPerColumn) + (cc * nodesPerLayer)][3],
			solidNodeIDs[0 + aa + (bb * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3],
			solidNodeIDs[1 + aa + (bb * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3],
			solidNodeIDs[1 + aa + ((bb + 1) * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3],
			solidNodeIDs[0 + aa + ((bb + 1) * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3]
						 ];

		if (counter % 2000 === 0){
			Message("soidnodeID");
			Message("a b c");
			Message(aa);
			Message(bb);
			Message(cc);
			//Message(solidNodeIDs[0 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)]);
			Message(solidNodeIDs[0 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][3]);
			Message(solidNodeIDs[1 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][3]);
			Message(solidNodeIDs[1 + aa + ((bb + 1) * nodesPerColumn) + (cc * nodesPerLayer)][3]);
			Message(solidNodeIDs[0 + aa + ((bb + 1) * nodesPerColumn) + (cc * nodesPerLayer)][3]);
			Message(solidNodeIDs[0 + aa + (bb * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3]);
			Message(solidNodeIDs[1 + aa + (bb * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3]);
			Message(solidNodeIDs[1 + aa + ((bb + 1) * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3]);
			Message(solidNodeIDs[0 + aa + ((bb + 1) * nodesPerColumn) + ((cc + 1) * nodesPerLayer)][3]);
			

		}
		
		makeSolids(counter, 1000000, solidNodes, 4);	

		counter += 1;
		return counter;
	}

	

	const gateXArray = new Array();
	const gateYArray = new Array();
	
	for (var idx = 0; idx < volume.length; idx++)
	{
		gateXArray.push(getBoundingCoords(centreCoords[idx][0], boxSize[idx][0] + gridSize * 4));
		gateYArray.push(getBoundingCoords(centreCoords[idx][1], boxSize[idx][1] + gridSize * 4));
	}
	
	var nodesPerRow          = fullDomainNoOfNodes[0];
	var nodesPerColumn       = fullDomainNoOfNodes[1];
	var numberOfLayers       = Math.floor((debrisHeight - solidStarting) / solidDepth) + 2;

	var nodesPerLayer        = nodesPerRow * nodesPerColumn;
	
	var counter              = 0;
	
	for (var aa = 0; aa < nodesPerColumn - 1; aa++)
	{
		for (var bb = 0; bb < nodesPerRow - 1; bb++)
		{
			for (var cc = 0; cc < numberOfLayers - 1; cc++) // numberOfLayers - 1
			{
				if (cc < numberOfLayers - 5)
				{
					counter = getSolidCoordinates()
				}
				else
				{
					var xCoord = (solidNodeIDs[0 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][0]
						    + solidNodeIDs[1 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][0])
						    / 2;
					var yCoord = (solidNodeIDs[0 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][1]
						    + solidNodeIDs[1 + aa + (bb * nodesPerColumn) + (cc * nodesPerLayer)][1])
						    / 2;
					
					for (var idx = 0; idx < volume.length; idx++)
					{
						// Remove this from this loop...
						const xCoords = getBoundingCoords(centreCoords[idx][0], boxSize[idx][0] + gridSize * 4);
						const yCoords = getBoundingCoords(centreCoords[idx][1], boxSize[idx][1] + gridSize * 4);
						
						if (xCoord > gateXArray[idx][0] && xCoord < gateXArray[idx][1] 
						 && yCoord > gateYArray[idx][0] && yCoord < gateYArray[idx][1])
						 {
							counter = getSolidCoordinates()
						 }
					}

				}
			}
		}
	}
					
}

function getAllNodes()
{
	const nodeArray          = new Array();
	var numberOfNodes        = getCurrentNumberOfNodes();
	var n                    = Node.First(m);

	for (var aa = 0; aa < numberOfNodes; aa++)
	{
		nodeArray.push([n.x, n.y, n.z, n.nid]);
		var n = n.Next();
	}
	
	return nodeArray;
}

function getAllNodesInTopography()
{
	const nodeArray          = new Array();
	var numberOfNodes        = getCurrentNumberOfNodes();
	var n                    = Node.First(m);

	for (var aa = 0; aa < numberOfNodes; aa++)
	{
		var xrefs = n.Xrefs();

		for (var t = 0; t < xrefs.numtypes; t++)
		{
			var type = xrefs.GetType(t);
			var s = 0;

			if (type == "SHELL")
			{
				var id = xrefs.GetItemID(type, 0);
				s = Shell.GetFromID(m, id);

				if (s.pid == 1) // only get part #1, topography.
				{
					nodeArray.push([n.x, n.y, n.z, n.nid]);
				}
			}
		}
		var n = n.Next();
	}
	return nodeArray;
}

function getNoOfNodesInTopography()
{
	const nodeArray          = new Array();
	var numberOfNodes        = getCurrentNumberOfNodes();
	var n                    = Node.First(m);
	var counter              = 0;

	for (var aa = 0; aa < numberOfNodes; aa++)
	{
		var xrefs = n.Xrefs();

		for (var t = 0; t < xrefs.numtypes; t++)
		{
			var type = xrefs.GetType(t);
			var s = 0;

			if (type == "SHELL")
			{
				var id = xrefs.GetItemID(type, 0);
				s = Shell.GetFromID(m, id);

				if (s.pid == 1) // only get part #1, topography.
				{
					counter += 1;
				}
			}
		}
		var n = n.Next();
	}
	return counter;
}

function findNodesForSource(xCoords, yCoords)
{
	//Message("can get to findnodesfor source");

	const localCoords        = new Array();
	var numberOfNodes        = getCurrentNumberOfNodes();

	//Message("can get to numberofNodes");

	var n                    = Node.First(m);

	//Message("can get to var n");

	for (var aa = 0; aa < numberOfNodes; aa++)
	{
		var xrefs = n.Xrefs();

		//Message("can get into for outer loop");

		for (var t = 0; t < xrefs.numtypes; t++)
		{
			var type = xrefs.GetType(t);
			var s = 0;

			//Message("can get into for inner for loop");

			if (type == "SHELL")
			{

				//Message("can get into in condition shell");

				var id = xrefs.GetItemID(type, 0);
				s = Shell.GetFromID(m, id);

				if (s.pid == 1) // only get part #1, topography.
				{	
					//Message("can get into in condition spid = 1");

					if (n.x >= xCoords[0] && 
						n.x <= xCoords[1] &&
						n.y >= yCoords[0] && 
						n.y <= yCoords[1])
					{
							// Message("can get into in local coor pushh");
							localCoords.push([n.x, n.y, n.z, n.nid]);
					}
				}
			}
		}
		
		var n = n.Next();	
	}

	return localCoords;
}

function findEdgeNodesForSource(xCoords, yCoords, nodesForLidCoords)
{
	var numberOfLidNodes    = nodesForLidCoords.length;
	const nodesOnEdgeCoords = new Array();
	
//	Message(numberOfLidNodes);
	
	for (var aa = 0; aa < numberOfLidNodes; aa++)
	{
		const distFromEdge = [
			Math.abs(nodesForLidCoords[aa][0] - xCoords[0]),
			Math.abs(nodesForLidCoords[aa][0] - xCoords[1]),
			Math.abs(nodesForLidCoords[aa][1] - yCoords[0]),
			Math.abs(nodesForLidCoords[aa][1] - yCoords[1])			
		];
		
		var nodesInRangeDistFromEdge = Math.min.apply(null, distFromEdge);

		if (nodesInRangeDistFromEdge <= edgeThreshold)
		{
			nodesOnEdgeCoords.push(nodesForLidCoords[aa]);
		}
	}
//	Message(nodesOnEdgeCoords.length);
	return nodesOnEdgeCoords;
}

function reorderNodesOnEdgeCoords(nodesOnEdgeCoords)
{
	const reorderedNodesOnEdgeCoords = new Array();

	var numberOfNodes = nodesOnEdgeCoords.length;
//	Message(numberOfNodes);
	reorderedNodesOnEdgeCoords[0] = nodesOnEdgeCoords[0];
	const idxer = new Array();
	idxer[0] = 0;
	
	for (var aa = 0; aa < numberOfNodes; aa++)
		for (var bb = 0; bb < numberOfNodes; bb++)
		{
			// Fixed a bug here relating to gridSize, but not sure why it happened.
			if (!idxer.includes(bb) &&
			   (Math.abs(nodesOnEdgeCoords[idxer.slice(-1)][0] - nodesOnEdgeCoords[bb][0]) +
				Math.abs(nodesOnEdgeCoords[idxer.slice(-1)][1] - nodesOnEdgeCoords[bb][1])) <= gridSize * 1.5)
			   {
					idxer.push(bb);
					reorderedNodesOnEdgeCoords.push(nodesOnEdgeCoords[bb]);
					break;
			   }
		}
//	Message(reorderedNodesOnEdgeCoords.length);
	return reorderedNodesOnEdgeCoords;
}


////////////////////////////////////////////////////////////////////

function createLidNodes(nodesForLidCoords)
{
	const lidNodeIDs = new Array();
	var numberOfNodes = getCurrentNumberOfNodes();

	for (var aa = 0; aa < nodesForLidCoords.length; aa++)
	{
		lidNodeIDs.push(numberOfNodes + aa + 1);
		
		var n = new Node(m,
			numberOfNodes + aa + 1, 
			nodesForLidCoords[aa][0], 
			nodesForLidCoords[aa][1],
			nodesForLidCoords[aa][2] + lidHeight);
	}
	return lidNodeIDs;
}

function addLidShells(fullBoxNoOfNodes, lidNodeIDs, idx)
{
	var numberOfShells = getCurrentNumberOfShells();

	var counter = 1;
	
	var nodesPerRow          = fullBoxNoOfNodes[0];
	var nodesPerColumn       = fullBoxNoOfNodes[1];

	for (var aa = 0; aa < nodesPerRow - 1; aa++) // nodesPerRow - 1
	{
		for (var bb = 0; bb < nodesPerColumn - 1; bb++) // nodesPerColumn - 1
		{
			const shellNodes = [lidNodeIDs[0 + bb + ((aa + 1) * nodesPerColumn)],
								lidNodeIDs[1 + bb + ((aa + 1) * nodesPerColumn)],
								lidNodeIDs[1 + bb + (aa * nodesPerColumn)],
								lidNodeIDs[0 + bb + (aa * nodesPerColumn)]
								];
		
			makeShells(counter, numberOfShells, shellNodes, 11 + idx * 2 + 1);

			counter += 1;
		}
	}
}

////////////////////////////////////////////////////////////////////

function createGateNodes(reorderedNodesOnEdgeCoords)
{
	const gateNodeIDs = new Array();
	var numberOfNodes = getCurrentNumberOfNodes();
	
	var numberOfNodeColumns = reorderedNodesOnEdgeCoords.length;
	var noOfGateHeightNodes = Math.round(gateHeight / gateMeshHeight) + 1;
	var gateStartingPoint   = -gateHeight / 2;
	
	var counter = 0;
	for (var aa = 0; aa < numberOfNodeColumns; aa++)
	{
		for (var bb = 0; bb < noOfGateHeightNodes; bb++)
		{
			gateNodeIDs.push(numberOfNodes + counter + 1);
			
			var n = new Node(m, 
				numberOfNodes + counter + 1, 
				reorderedNodesOnEdgeCoords[aa][0], 
				reorderedNodesOnEdgeCoords[aa][1],
				reorderedNodesOnEdgeCoords[aa][2] + lidHeight + gateStartingPoint + bb * gateMeshHeight);
			
			counter += 1;
		}
	}
	return gateNodeIDs;
}

function makeShells(counter, shellIDIncrement, shellNodes, partNumber)
{
	var s = new Shell(m, counter + shellIDIncrement + 1, partNumber, 
			shellNodes[0],
			shellNodes[1],
			shellNodes[2],
			shellNodes[3]);
}

function addGateShells(fullBoxNoOfNodes, reorderedNodesOnEdgeCoords, gateNodeIDs, idx)
{
	var numberOfShells = getCurrentNumberOfShells();

	var numberOfNodeColumns = reorderedNodesOnEdgeCoords.length;
	var noOfGateHeightNodes = Math.round(gateHeight / gateMeshHeight) + 1;
	// Do all but the last 'wall'.
	var counter = 1;
	for (var aa = 0; aa < numberOfNodeColumns - 1; aa++)
	{
		for (var bb = 0; bb < noOfGateHeightNodes - 1; bb++)
		{
			const shellNodes = [gateNodeIDs[0 + bb + (aa * (noOfGateHeightNodes))],
								gateNodeIDs[1 + bb + (aa * (noOfGateHeightNodes))],
								gateNodeIDs[1 + bb + ((aa + 1) * (noOfGateHeightNodes))],
								gateNodeIDs[0 + bb + ((aa + 1) * (noOfGateHeightNodes))]
								];

			makeShells(counter, numberOfShells, shellNodes, 11 + idx * 2);
				
			counter += 1;
		}
	}

	// Now do the last wall.
	aa = numberOfNodeColumns - 1;
	for (var bb = 0; bb < noOfGateHeightNodes - 1; bb++)
	{
		const shellNodes = [gateNodeIDs[0 + bb + (aa * (noOfGateHeightNodes))],
							gateNodeIDs[1 + bb + (aa * (noOfGateHeightNodes))],
							gateNodeIDs[1 + bb + ((0) * (noOfGateHeightNodes))],
							gateNodeIDs[0 + bb + ((0) * (noOfGateHeightNodes))]
							];
							
		makeShells(counter, numberOfShells, shellNodes, 11 + idx * 2);
			
		counter += 1;
	}
}

function getDebrisHeight(volume, boxSize)
{
	//Message("Now getting DebrisHeight");
	var debrisHeight = 0.0;
	for (var aa = 0; aa < volume.length; aa++)
	{
		var tempHeight = volume[aa] / (boxSize[aa][0] * boxSize[aa][1]);
		if (tempHeight > debrisHeight)
		{
			debrisHeight = tempHeight;
		}
	}
	return debrisHeight;
}

////////////////////////////////////////////////////////////////////
// PROGRAM
////////////////////////////////////////////////////////////////////

var debrisHeight = getDebrisHeight(volume, boxSize);

const nodeArray                  = getAllNodesInTopography();
const fullDomainNoOfNodes        = getBoxBounds(nodeArray);
const solidNodeIDs               = copyNodesForSolids(nodeArray, debrisHeight);

createSolids(solidNodeIDs, fullDomainNoOfNodes);


for (var idx = 0; idx < volume.length; idx++) // 
{
	
	var lidHeight  = volume[idx] / (boxSize[idx][0] * boxSize[idx][1]);

	//Message(idx.toString() + " it is still working after lidheight");

	var gateHeight = lidHeight * 2.5; // so 10 m above surface 

	//Message(idx.toString() + " it is still working aftergateheight");

	const xCoords                    = getBoundingCoords(centreCoords[idx][0], boxSize[idx][0]);
	const yCoords                    = getBoundingCoords(centreCoords[idx][1], boxSize[idx][1]);

	//Message(idx.toString() + " it is still working after XYcoords");

	const nodesForLidCoords          = findNodesForSource(xCoords, yCoords);

	//Message(idx.toString() + " it is still working after nodesforlidcoords");

	const nodesOnEdgeCoords          = findEdgeNodesForSource(xCoords, yCoords, nodesForLidCoords);

	//Message(idx.toString() + " it is still working after nodesonedgecoords");

	const reorderedNodesOnEdgeCoords = reorderNodesOnEdgeCoords(nodesOnEdgeCoords);

	//Message(idx.toString() + " it is still working after reorderedNodesOnEdgeCoords");

	// Should be similar to what we originally defined.
	const fullBoxNoOfNodes           = getBoxBounds(nodesForLidCoords);

	//Message(idx.toString() + " it is still working after fullBoxNoOfNodes");

	const lidNodeIDs                 = createLidNodes(nodesForLidCoords);
	addLidShells(fullBoxNoOfNodes, lidNodeIDs, idx)

	//Message(idx.toString() + " it is still working after addidshells");

	const gateNodeIDs                = createGateNodes(reorderedNodesOnEdgeCoords);

	//Message(idx.toString() + " it is still working after getnodeids");

	addGateShells(fullBoxNoOfNodes, reorderedNodesOnEdgeCoords, gateNodeIDs, idx);

	//Message(idx.toString() + " it is still working after addgateshells");

}



m.UpdateGraphics();

// node_df = pd.read_csv("node_array.csv")
// node_array = node_df["Node"]

// import the csv-parse module
