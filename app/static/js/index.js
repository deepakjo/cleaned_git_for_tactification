
$(document).ready(function(){
    console.log("here");
    $('.action .right-image').css('background-image','url(' + background_img_url + ')');
}); 

$(function() {
    console.log("postPic");
    $('#fbId').width(100);
    $('#fbId').height(25);
});

$(function() {
    console.log("postPic");
    $('#twId').width(100);
    $('#twId').height(25);
});

function updateStatusCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      console.alert('Its connected');
    } else {
      // The person is not logged into your app or we are unable to tell.
        console.alert('Its not authorized');
    }
}

$(document).ready(function() {
    $.ajaxSetup({ cache: true });
    $.getScript('//connect.facebook.net/en_US/sdk.js', function(){
      FB.init({
        appId: '613455148848789',
        version: 'v2.7' // or v2.1, v2.2, v2.3, ...
      });     
      $('#loginbutton,#feedbutton').removeAttr('disabled');
      FB.getLoginStatus(updateStatusCallback);
    });
});