$( document ).ready(function() {

  // 遍历结果，然后逐条清除
  function removeItem(elem_id){
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
          video_str = video_str.replace('message', '<em>Top-' + ++i + '\tScore:' + scores[i]);
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
      url : '/upload' //服务器端的上传页面地址
  });
  var filename = '';

  //在实例对象上调用init()方法进行初始化
  uploader.init();

  //绑定各种事件，并在事件监听函数中做你想做的事
  uploader.bind('FilesAdded', function(uploader, files) {
      //每个事件监听函数都会传入一些很有用的参数，
      //我们可以利用这些参数提供的信息来做比如更新UI，提示上传进度等操作
    plupload.each(files, function (file) {
      filename = file.name;
      uploader.start();
    });
  });

  //上传中，显示进度条
  uploader.bind('UploadProgress', function(uploader, file) {
    $('#progress').css('width', file.percent+'%');
  });

  // 上传完成
  uploader.bind('UploadComplete', function(uploader, files) {
    plupload.each(files, function (file) {
      // alert(file.name + ' uploaded successfully!');
    })
  });

  // 上传出错
  uploader.bind('Error', function(uploader, errObject) { //上传出错的时候触发
    alert(errObject.code+errObject.message);
  });

  //最后给"开始上传"按钮注册事件
  $( "#start_upload" ).click(function(){
    var localize_str = $("#localize").val();
    console.log(localize_str);
    if (localize_str == '') {
      alert('Please input localize string first!')
      return;
    }
    if (filename == '') {
      alert('Please upload video file first!')
      return;
    }
    removeItem("localizationResult");
    
	  console.log(localize_str, filename);
    $.post( "/localize", {
        localize_str: JSON.stringify(localize_str),
        filename: JSON.stringify(filename)
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
              + '<source src="movie" type="video/mp4">'
              + '</video>'
              + '<p>message</p> </div>';
            video_str = str.replace('movie', '/static/videos/TACoS/splited/' + video_names[i]);
            video_str = video_str.replace('message', '<em>Top-' + ++i + '\tScore:' + scores[i]);
            $( "#localizationResult" ).append(video_str)
          };
        } else {
          $( "#localizationResult" ).append('<p>Do not find any related videos. Please try other queries.</p>')
        }
      });
  });

});
