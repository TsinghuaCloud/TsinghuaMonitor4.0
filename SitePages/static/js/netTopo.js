var canvas = document.getElementById('canvas');
var scene;
var topoInfo;
function resizeCanvas() {

	canvas.setAttribute("width", $('#content').attr("width"));
	canvas.setAttribute("height", $('#content').attr("height"));

};
$(document).ready(function() {
	// drawCanvas();
	// $(window).resize(resizeCanvas);
	// resizeCanvas();
	var stage = new JTopo.Stage(canvas);
	// 显示工具栏
	showJTopoToobar(stage);
	scene = new JTopo.Scene();
	stage.add(scene);
	getTopoInfo();
	setInterval(getTopoInfo,4000);
	//getTopoInfo();
});
function clickEvent(){
console.info("click");
};
function node(x, y, img,text) {
	var node = new JTopo.Node(text);
	node.setImage('/static/img/statistics/' + img, true);
	node.setLocation(x, y);
	//node.setCenterLocation(x,y);
	//node.text=text;
	node.text = text; // 文字
	//node.textPosition = 'Middle_Center';// 文字居中
	//node.textOffsetY = 8; // 文字向下偏移8个像素
	node.font = '1px 微软雅黑'; // 字体
	//node.setLocation(180, 100); // 位置
	//node.setSize(100, 60);  // 尺寸
	//node.borderRadius = 5; // 圆角
	//node.borderWidth = 2; // 边框的宽度
	//node.borderColor = '255,255,255'; //边框颜色            
	//node.alpha = 0; //透明度
	node.fontColor = "255,255,255";
	node.mouseover(function(){
		
		this.fontColor = "0,0,0";
				//this.zIndex=90;
		//console.info(this.zIndex);
	});
	node.mouseout(function(){
		
		this.fontColor = "255,255,255";
		//this.zIndex=100;
		//console.info(this.zIndex);
	});
	//node.fontColor=JTopo.util.randomColor();
	//node.zIndex=100;
	scene.add(node);
	return node;
}
function linkNode(nodeA, nodeZ,linktext) {
	var link;

		link = new JTopo.FoldLink(nodeA, nodeZ);
	
	//link.strokeColor="105,71,135";
	link.strokeColor=JTopo.util.randomColor();
	//link.direction = 'curve';
	link.arrowsRadius = 10;
	link.text=linktext;
	scene.add(link);
	return link;
}
//function hostLink(nodeA, nodeZ) {
//	var link = new JTopo.FlexionalLink(nodeA, nodeZ);
//	link.shadow = false;
//	link.offsetGap = 44;
//	link.arrowsRadius = 10;
//	scene.add(link);
//	return link;
//}
function createMyNode(refernode, index, xoffset, yoffset, picname,text,linktext) {
	var x;
	if (index % 2 == 1) {
		x = refernode.x + ((index - 1) / 2) * xoffset;
	} else {
		x = refernode.x - (index / 2) * xoffset;
	}
	var y = refernode.y + yoffset;
	// console.info("index"+index+"x"+x);
	var node_termp = node(x, y, picname,text);
	//node_termp.setCenterLocation(x,y);
	//linkNode(node_termp, refernode, true);
	linkNode(refernode, node_termp,linktext);
	return node_termp;
}

drawCanvas = function() {
	var stage = new JTopo.Stage(canvas);
	// 显示工具栏
	showJTopoToobar(stage);
	scene = new JTopo.Scene();
	// scene.background = '/static/img/bg.jpg';
	var w1 = node(500, 30, 'wanjet.png');
	var secondeNodes = new Array();
	var thirdNodesLeft = new Array();
	var thirdNodesright = new Array();
	for ( var i = 2; i <= 3; i++) {
		secondeNodes.push(createMyNode(w1, i, 200, 100, 'switch.png'));
	}
	for ( var i = 1; i <= 5; i++) {
		thirdNodesLeft.push(createMyNode(secondeNodes[0], i, 80, 100,
				'server.png'));
		thirdNodesright.push(createMyNode(secondeNodes[1], i, 80, 100,
				'server.png'));
	}
	stage.add(scene);
};
function drawOneNode(referNode, id,type,level) {
	var allSubNode = topoInfo[id];
	var index = 1;
	for ( var i = 0; i < allSubNode.length; i++) {
		var picName = '';
		var xoffset = 0;
		if (allSubNode[i].type == '1') {
			picName = 'switch.png';
			xoffset = 250;
			
		} else if (allSubNode[i].type == '2') {
			picName = 'server.png';
			xoffset = 150;
			
		}
		xoffset-=42*level;
		if(type=='1'&&allSubNode[i].type == '1'){
			index=2;
		}
		var node_temp = createMyNode(referNode, i + index, xoffset, 100,picName,allSubNode[i].toMac,allSubNode[i].frominOctets+","+allSubNode[i].fromoutOctets);
		if (topoInfo[allSubNode[i].toId] != null) {
			drawOneNode(node_temp, allSubNode[i].toId,allSubNode[i].type,level+1);
		}
	}
};
function getTopoInfo() {
	
	//scene.background = '/static/img/bg.jpg';
	$.ajax({
		url : "/api/getTopoInfo",
		dataType : "json",
		success : function(data) {
			topoInfo = data['data'];
			topoInfo = eval('(' + topoInfo + ')');
			scene.clear();
			var w1 = node(600, 30, 'switch.png');
			drawOneNode(w1, topoInfo.first.id,'1',0);
			
		}
	});
};
