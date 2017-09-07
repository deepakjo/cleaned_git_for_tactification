$(document).ready(function(){
  $("#myModal").on("shown.bs.modal",function(){
     $('#myModal').removeClass('in');
  })
})

function changeVideo(vId){
  var iframe=document.getElementById("iframeYoutube");
  iframe.src="https://www.youtube.com/embed/"+vId+"?html5=1";
  $("#myModal").modal("show");
}

