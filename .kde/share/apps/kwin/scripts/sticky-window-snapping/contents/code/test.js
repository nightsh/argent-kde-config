var config =
	{ enabledCurrently : true
	, enabledUsually : true
	, liveUpdate : true
	, opacityOfSnapped : 0.75
	};

/****************************************************************************/

init();

function init() {
	var clients = workspace.clientList(); 
	for (var i = 0; i < clients.length; i++) {
		connectClient(clients[i]);
	}
	workspace.clientAdded.connect(connectClient);
}

function connectClient(client) {
	if (compareRects(client.geometry, workspace.clientArea(workspace.MaximizeArea, client)))
		print("    maximized: " + client.caption);
	else
		print("not maximized: " + client.caption);
	r1 = client.geometry;
	r2 = copyRect(r1);
	r3 = copyRect(r1);
	r3.x = -44
	print(compareRects(r1, r2) + " " + compareRects(r1, r3) + " " + compareRects(r2, r3));
	print(shallowEquals(r1, r2) + " " + shallowEquals(r1, r3) + " " + shallowEquals(r2, r3));
}

function compareRects(r1, r2) {
	return r1.x === r2.x && r1.y === r2.y && r1.width === r2.width && r1.height === r2.height;
}

function copyRect(r) {
	return { x: r.x, y: r.y, width: r.width, height: r.height };
}

function shallowEquals(x, y) {
	if (Object.keys(x).length !== Object.keys(y).length) {
		return false;
	}
	for (var p in x) {
		if (x[p] !== y[p]) {
			return false;
		}
	}
	return true;
}






	if (client.shade) {
		print("shaded: " + client.caption);
		print("new:\t" + geometry.x + "\t" + geometry.y + "\t" + geometry.width + "\t" + geometry.height);
		print("cur:\t" + client.geometry.x + "\t" + client.geometry.y + "\t" + client.geometry.width + "\t" + client.geometry.height);
		print("min:\t\t" + client.minSize.w + "\t\t" + client.minSize.h);
		print("max:\t\t" + client.maxSize.w + "\t\t" + client.maxSize.h);
	}
