var canvas = document.getElementById('canvas');
var scene;
function resizeCanvas() {

	canvas.setAttribute("width", $('#content').attr("width"));
	canvas.setAttribute("height", $('#content').attr("height"));

};
$(document).ready(function() {
	drawCanvas();
//	$(window).resize(resizeCanvas);
//	resizeCanvas();

});
function node(x, y, img) {
	var node = new JTopo.Node();
	node.setImage('/static/img/statistics/' + img, true);
	node.setLocation(x, y);
	scene.add(node);
	return node;
}
function linkNode(nodeA, nodeZ, f) {
	var link;
	if (f) {
		link = new JTopo.FoldLink(nodeA, nodeZ);
	} else {
		link = new JTopo.Link(nodeA, nodeZ);
	}
	link.direction = 'curve';
	scene.add(link);
	return link;
}
function hostLink(nodeA, nodeZ) {
	var link = new JTopo.FlexionalLink(nodeA, nodeZ);
	link.shadow = false;
	link.offsetGap = 44;
	scene.add(link);
	return link;
}
function createMyNode(refernode,index,xoffset,yoffset,picname) {
    
	var x;
	if(index%2==1){
		x=refernode.x+((index-1)/2)*xoffset;
	}else{
		x=refernode.x-(index/2)*xoffset;
	}
	var y=refernode.y+	yoffset;
	//console.info("index"+index+"x"+x);
	var node_termp=node(x,y,picname);
	linkNode(node_termp, refernode,true);
	return node_termp;
}

drawCanvas = function() {
	var stage = new JTopo.Stage(canvas);
	//显示工具栏
	showJTopoToobar(stage);
	scene = new JTopo.Scene();
	//scene.background = '/static/img/bg.jpg';
	var w1 = node(500, 30, 'wanjet.png');
	var secondeNodes = new Array();
	var thirdNodesLeft = new Array();
	var thirdNodesright = new Array();
	for(var i=2;i<=3;i++){
		secondeNodes.push(createMyNode(w1,i,200,100,'wanjet.png'));
	}
	for(var i=1;i<=5;i++){
		thirdNodesLeft.push(createMyNode(secondeNodes[0],i,80,100,'server.png'));
		thirdNodesright.push(createMyNode(secondeNodes[1],i,80,100,'server.png'));
	}
	stage.add(scene);
};