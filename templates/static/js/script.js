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

// 原有画图项目的方法，清空数据
  $( "#clearButton" ).click(function(){
    clearCanvas();
  });

  // 原有画图项目的方法，发送数据
  $( "#sendButton" ).click(function(){
    getData();
  });

  // 遍历结果，然后逐条清除
  function removeItem(var elem_id){
    var e = document.getElementById(elem_id);
    var first = e.firstElementChild;
    while (first) {
      first.remove();
      first = e.firstElementChild;
    }
  }

  // 发起搜索请求（先清空原有结果）
  $( "#searchButton" ).click(function(){
    removeItem("searchResult");
    sendSearchData();
  });

  // 发送搜索数据
  function sendSearchData() {
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
          var str = '<div> <video width="280" height="230" controls>'
            + '<source src="movie.mp4" type="video/mp4">'
            + '</video>'
            + '<p>message</p> </div>';
          video_str = str.replace('movie', '/static/videos/' + video_names[i]);
          video_str = video_str.replace('message', '<em>Top-' + i + '\t<em>Score:' + scores[i]);
          $( "#searchResult" ).append(video_str)
        };
      } else {
        $( "#searchResult" ).append('<p>Do not find any related videos. Please try other queries.</p>')
      }
    });
  };

  //实例化一个plupload上传对象
  var uploader = new plupload.Uploader({
      browse_button : 'browse', //触发文件选择对话框的按钮，为那个元素id
      url : '/localize' //服务器端的上传页面地址
  });

  //在实例对象上调用init()方法进行初始化
  uploader.init();

  //绑定各种事件，并在事件监听函数中做你想做的事
  uploader.bind('FilesAdded', function(uploader, files) {
      //每个事件监听函数都会传入一些很有用的参数，
      //我们可以利用这些参数提供的信息来做比如更新UI，提示上传进度等操作
    plupload.each(files, function (file) {
      uploader_video.start();
    });
  });

  //上传中，显示进度条
  uploader.bind('UploadProgress', function(uploader, file) {
    $('#Progress').css('width', file.percent+'%');
  };

  uploader.bind('Error', function(uploader, errObject) { //上传出错的时候触发
        alert(errObject.code+errObject.message);
  });

  //最后给"开始上传"按钮注册事件
  document.getElementById('start_upload').onclick = function(){
    removeItem("localizationResult");
    uploader.start(); //调用实例对象的start()方法开始上传文件，当然你也可以在其他地方调用该方法
    alert(file.name);
    sendLocalizationData(file.name);
  };

  // 发送定位数据
  function sendLocalizationData(var filename) {
	var localize_str = $("#localize").val();
	console.log(localize_str, filename);
	$.post( "/localize", {
      localize_str: JSON.stringify(localize_str)
      upload_video: JSON.stringify(filename)
    }, function(err, req, resp){
      var video_names = resp["responseJSON"]['video_names'];
      var scores = resp["responseJSON"]['scores'];
      var idxs = resp["responseJSON"]['idxs'];
      console.log(video_names)
      console.log(scores)
      console.log(idxs)
      if (Array.isArray(video_names) && video_names.length) {
        for(var i in idxs) {
          var str = '<div> <video width="280" height="230" controls>'
            + '<source src="movie.mp4" type="video/mp4">'
            + '</video>'
            + '<p>message</p> </div>';
          video_str = str.replace('movie', '/static/videos/' + video_names[i]);
          video_str = video_str.replace('message', '<em>Top-' + i + '\t<em>Score:' + scores[i]);
          $( "#localizationResult" ).append(video_str)
        };
      } else {
        $( "#localizationResult" ).append('<p>Do not find any related videos. Please try other queries.</p>')
      }
    });
  }

});
