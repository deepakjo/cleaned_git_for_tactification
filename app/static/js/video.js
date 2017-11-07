$(document).ready(function(){
  $("#myModal").on("shown.bs.modal",function(){
     $('#myModal').removeClass('in');
  })
})

$("#myModal").on('hidden.bs.modal', function (e) {
  $("#myModal iframe").attr("src", $("#myModal iframe").attr("src"));
});

function inspireVideo(vId){
  var iframe=document.getElementById("iframeYoutube");
  iframe.src="https://www.youtube.com/embed/"+vId+"?html5=1";
  $("#myModal").modal("show");
}

