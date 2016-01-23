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
	link.direction = 'vertical';
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
drawCanvas = function() {
	var stage = new JTopo.Stage(canvas);
	//显示工具栏
	showJTopoToobar(stage);
	scene = new JTopo.Scene();
	scene.background = '/static/img/bg.jpg';

	var w1 = node(524, 167, 'wanjet.png');

	var w2 = node(324, 277, 'wanjet.png');
	
	var h1 = node(218, 420, 'host.png');
	h1.alarm = '';
	linkNode(h1, w2,true);
	//linkNode(h1, w2,true);
	var h2 = node(292, 420, 'host.png');
	linkNode(h2, w2,true);
	var h3 = node(366, 420, 'host.png');
	h3.alarm = '二级告警';
	linkNode(h3, w2,true);
	var h4 = node(447, 420, 'host.png');
	linkNode(h4, w2,true);
	var h5 = node(515, 420, 'host.png');
	h5.alarm = '1M';
	linkNode(h5, w2,true);
	
	setInterval(function() {
		if (h3.alarm == '二级告警') {
			h3.alarm = null;
		} else {
			h3.alarm = '二级告警'
		}
	}, 600);
	
	var w21 = node(724, 277, 'wanjet.png');
	//linkNode(c2, w21);

	var h11 = node(618, 420, 'host.png');
	h11.alarm = '';
	linkNode(h11, w21,true);
	var h21 = node(692, 420, 'host.png');
	linkNode(h21, w21,true);
	var h31 = node(766, 420, 'host.png');
	h31.alarm = '二级告警';
	linkNode(h31, w21,true);
	var h41 = node(847, 420, 'host.png');
	linkNode(h41, w21,true);
	var h51 = node(915, 420, 'host.png');
	h51.alarm = '1M';
	linkNode(h51, w21,true);
	setInterval(function() {
		if (h31.alarm == '二级告警') {
			h31.alarm = null;
		} else {
			h31.alarm = '二级告警'
		}
	}, 600);
	linkNode(w2, w1,true);
	linkNode(w21, w1,true);
	
	stage.add(scene);
};