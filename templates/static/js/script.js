$( document ).ready(function() {
  // 原有画图项目的方法，创建新的画图框
   function createCanvas(parent, width, height) {
    var canvas = document.getElementById("inputCanvas");
    canvas.context = canvas.getContext('2d');
    return canvas;
  }

  // 原有画图项目的方法
  function init(container, width, height, fillColor) {
    var canvas = createCanvas(container, width, height);
    var ctx = canvas.context;
    ctx.fillCircle = function(x, y, radius, fillColor) {
      this.fillStyle = fillColor;
      this.beginPath();
      this.moveTo(x, y);
      this.arc(x, y, radius, 0, Math.PI * 2, false);
      this.fill();
    };
    ctx.clearTo = function(fillColor) {
      ctx.fillStyle = fillColor;
      ctx.fillRect(0, 0, width, height);
    };
    ctx.clearTo("#fff");

    canvas.onmousemove = function(e) {
      if (!canvas.isDrawing) {
        return;
      }
      var x = e.pageX - this.offsetLeft;
      var y = e.pageY - this.offsetTop;
      var radius = 10;
      var fillColor = 'rgb(102,153,255)';
      ctx.fillCircle(x, y, radius, fillColor);
    };
    canvas.onmousedown = function(e) {
      canvas.isDrawing = true;
    };
    canvas.onmouseup = function(e) {
      canvas.isDrawing = false;
    };
  }

//  var container = document.getElementById('canvas');
//  init(container, 200, 200, '#ddd');

  // 原有画图项目的方法，清理画图框中的数据
  function clearCanvas() {
    var canvas = document.getElementById("inputCanvas");
    var ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
  }

  // 原有画图项目的方法，获得画图框中的数据
  function getData() {
    console.log('hello');
    var canvas = document.getElementById("inputCanvas");
    var imageData = canvas.context.getImageData(0, 0, canvas.width, canvas.height);
    var data = imageData.data;
    var outputData = []
    for(var i = 0; i < data.length; i += 4) {
      var brightness = 0.34 * data[i] + 0.5 * data[i + 1] + 0.16 * data[i + 2];
      outputData.push(brightness);
    }
    $.post( "/postmethod", {
      canvas_data: JSON.stringify(outputData)
    }, function(err, req, resp){
      window.location.href = "/results/"+resp["responseJSON"]["uuid"];  
    });
  }

  // 遍历结果，然后逐条清除
  function removeItem(){
    var e = document.getElementById("result");
    var first = e.firstElementChild;
    while (first) {
      first.remove();
      first = e.firstElementChild;
    }
    //e.firstElementChild can be used.
//    var child = e.lastElementChild;
//    while (child) {
//        e.removeChild(child);
//        child = e.lastElementChild;
//    }
  }

  // 发送请求
  function sendData() {
    // var data = document.getElementById("search");
	var data = $("#search").val();
	console.log(data);
	$.post( "/search", {
      search_data: JSON.stringify(data)
    }, function(err, req, resp){
      var video_names = resp["responseJSON"]['video_names'];
      var scores = resp["responseJSON"]['scores'];
      var idxs = resp["responseJSON"]['idxs'];
      console.log(video_names)
      console.log(scores)
      console.log(idxs)
      if (Array.isArray(video_names) && video_names.length) {
        for(var i in idxs) {
//        var li = "<li>";
          var str = '<video width="640" height="480" controls> <source src="movie.mp4" type="video/mp4"></video><p>message</p>';
          video_str = str.replace('movie', '/static/videos/' + video_names[i]);
          video_str = video_str.replace('message', 'Video:' + video_names[i].substr(5) + '.mp4\tScore:' + scores[i]);
          $( "#result" ).append(video_str)
        };
      } else {
        $( "#result" ).append('<p>Do not find any related videos. Please try other queries.</p>')
      }
//      $( "#result" ).text(resp["responseJSON"]['status'] + resp["responseJSON"]['data']);
    });
  }

  // 原有画图项目的方法，清空数据
  $( "#clearButton" ).click(function(){
    clearCanvas();
  });

  // 原有画图项目的方法，发送数据
  $( "#sendButton" ).click(function(){
    getData();
  });

  // 发起搜索请求（先清空原有结果）
  $( "#searchButton" ).click(function(){
    removeItem();
    sendData();
  });
});
