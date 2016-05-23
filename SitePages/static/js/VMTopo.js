var canvas = document.getElementById('canvas');
var scene;
var vmtopoInfo;

var ip_node = function() {
    var no;
    var x = 0;
    var y = 0;
    this.set_node = function(x,y,img,text){
        this.no = node(x,y,img,text);
        this.x = x;
        this.y = y;
    };
    this.get_node = function(){
        return this.no;
    };
    this.get_x = function(){
        return this.x;
    };
    this.get_y = function(){
        return this.y;
    }
};

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
	getVM_TopoInfo();
	setInterval(getVM_TopoInfo,10000);
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
	node.fontColor = "0,0,0";
	//node.mouseover(function(){

		//this.fontColor = "0,0,0";
				//this.zIndex=90;
		//console.info(this.zIndex);
	//});
	//node.mouseout(function(){

		//this.fontColor = "255,255,255";
		//this.zIndex=100;
		//console.info(this.zIndex);
	//});
	//node.fontColor=JTopo.util.randomColor();
	//node.zIndex=100;
	scene.add(node);
	return node;
}
function linkNode(nodeA, nodeZ,linktext) {
	var link;
    link = new JTopo.Link(nodeA, nodeZ);
	//link.strokeColor="105,71,135";
	link.strokeColor=JTopo.util.randomColor();
	//link.direction = 'curve';
	//link.arrowsRadius = 10;
	link.text=linktext;
	scene.add(link);
	return link;
}

function drawNode(topo,len) {
    var node_array = new Array();
    var offsetx;
    var offsety;
    var c1=1;
    var c2=-1;
    var c22=1;
    //console.info(len);
    for (var i=0;i<len-1;i++)
    {
        var temp = topo[i].split(' ');
        var img;
        console.info(temp);
        if (i==0)
        {
            var n1 = new ip_node();
            if (temp[0]=="externNet")
            {img = "外网.png";}
            else
            {img = "虚拟机.png";}
            n1.set_node(90,20,img,temp[0]);
            node_array[temp[0]]=n1;

            var n2 = new ip_node();
            if (temp[1]=="externNet")
            {img = "外网.png";}
            else
            {img = "虚拟机.png";}
            n2.set_node(190,20,img,temp[1]);
            node_array[temp[1]]=n2;
            linkNode(n1.get_node(),n2.get_node());
            offsetx=160;
            offsety=20;
        }
        //for (var key in node_array)
        //{console.info(key);}
        else
        {
            if (node_array.hasOwnProperty(temp[0])==false && node_array.hasOwnProperty(temp[1])==false)
            {

                var na = new ip_node();
                if (temp[0]=="externNet")
                {img = "外网.png";}
                else
                {img = "虚拟机.png";}
                na.set_node(offsetx+c1*100,offsety+c1*20,img,temp[0]);
                node_array[temp[0]]=na;

                var nb = new ip_node();
                if (temp[1]=="externNet")
                {img = "外网.png";}
                else
                {img = "虚拟机.png";}
                nb.set_node(offsetx+(c1+1)*100,offsety+c1*20,img,temp[1]);
                node_array[temp[1]]=nb;
                linkNode(na.get_node(),nb.get_node());
                c1++;
            }
            else if (node_array.hasOwnProperty(temp[0])==true && node_array.hasOwnProperty(temp[1])==false)
            {

                var n3 = new ip_node();
                if (temp[1]=="externNet")
                {img = "外网.png";}
                else
                {img = "虚拟机.png";}
                n3.set_node(node_array[temp[0]].get_x()+c2*60,node_array[temp[0]].get_y()+c22*65,img,temp[1]);
                node_array[temp[1]]=n3;

                linkNode(n3.get_node(),node_array[temp[0]].get_node());
                c2++;
                c22++;
                //c3++;
                //c33++;
            }
            else if (node_array.hasOwnProperty(temp[0])==false && node_array.hasOwnProperty(temp[1])==true)
            {

                var n4 = new ip_node();
                if (temp[0]=="externNet")
                {img = "外网.png";}
                else
                {img = "虚拟机.png";}
                n4.set_node(node_array[temp[1]].get_x()+c2*60,node_array[temp[1]].get_y()+c22*65,img,temp[0]);
                node_array[temp[0]]=n4;

                linkNode(n4.get_node(),node_array[temp[1]].get_node());
                //c3++;
                //c33++;
                c2++;
                c22++;
            }
            else if (node_array.hasOwnProperty(temp[0])==true && node_array.hasOwnProperty(temp[1])==true)
            {
                linkNode(node_array[temp[0]].get_node(),node_array[temp[1]].get_node());
            }
        }
    }
    //how to delete the last time de array
};
function getVM_TopoInfo() {

	//scene.background = '/static/img/bg.jpg';
	$.ajax({
		url : "/api/getVM_TopoInfo",
		dataType : "",
		success : function(data) {
			vmtopoInfo = data.split(',');  //vmtopoInfo is an array
			//console.info(vmtopoInfo);
			scene.clear();
			drawNode(vmtopoInfo,vmtopoInfo.length);
		}
	});
};
