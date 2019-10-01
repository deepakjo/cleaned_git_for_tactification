var id = 0;

function insertAfter(referenceNode, newNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

function addElement(comment_in_json) {
    var cur_node_id = id + 1;
    var main_div_elem = $('<div />', {id : 'div'.concat(cur_node_id), "class" : "row"});
    
    var col_md_8_elem = $('<div />', {id : 'col_md_8_elem'.concat(cur_node_id), "class" : "col-md-8"});
    main_div_elem.append(col_md_8_elem);  
    var media_elem = $('<div />', {id : 'media_elem'.concat(cur_node_id), "class" : "media"});
    $(col_md_8_elem).append(media_elem);
    var media_left_top_elem = $('<div />', {id : 'media_left_top_elem'.concat(cur_node_id), "class" : "media-left media-top"});
    $(media_elem).append(media_left_top_elem);

    var img_media_elem = $('<img>', {id : 'img_media_elem'.concat(cur_node_id), "class": "media-object", 
                                     src : comment_in_json['pfl_pic'],
                                     css : {width : "60px"}}); 
    $(media_left_top_elem).append(img_media_elem);                                       


    var media_body_elem = $('<div />', {id : 'media_body_elem'.concat(cur_node_id), "class" : "media-body"});    
    var h4_body_elem = $('<div />', {id : 'h4_body_elem'.concat(cur_node_id), "class" : "media-heading"});
    $(media_body_elem).append(h4_body_elem);
    
    var strong_elem = $('<strong />', {id : 'strong_elem'.concat(cur_node_id), text : comment_in_json['uname'],                                           
                                       css : {color : 'black', fontSize : "18px"}});
    var time_elem = $('<h4 />', {id : 'time_elem'.concat(cur_node_id), 
                                 css : {fontSize : "14px", color: "black"},
                                 text : moment(comment_in_json['ts']).fromNow(refresh = true)});
    $(h4_body_elem).append(strong_elem, time_elem);

    var p_comment_elem = $('<p />', {id : 'p_comment_elem'.concat(cur_node_id)});
    var h4_html_id = 'h4_comment_elem'.concat(cur_node_id);
    var h4_comment_elem = $('<h4 />', {id : h4_html_id, 
                                       //"class" : "blog-comment-ajax",
                                       text : comment_in_json['comment']});

    $(p_comment_elem).append(h4_comment_elem);
    $(media_elem).append(media_body_elem);
    $(media_body_elem).append(p_comment_elem);

    var prev_div = document.getElementById("div".concat(id));
    $(main_div_elem).insertAfter(prev_div);

    //if (comment_in_json['is_anon'] === 1) {
    //    $('#div'.concat(id)).append(main_div_elem);
    //} else {
    //    $('#div'.concat(id)).append(main_div_elem);        
    //}    

    //var value = $(".blog-comment-ajax").text();
    //$(".blog-comment-ajax").html(comment_in_json['comment']);

    //var value = $(".blog-comment-ajax").text();

    var value = $(h4_comment_elem).text();
    $(h4_comment_elem).html(comment_in_json['comment']);

    var value = $(h4_comment_elem).text();
    id = id + 1;
}

$(function() { 
    $('#submitWithName').click(function() {
        var uname = $('input[name="uname"]').val();
        var comment = $('textarea[name="comment"]').val();
        var no_of_comments;

        if (uname == '' || comment == '') {
            alert("Name and Comment should not be empty");
            return;
        }

        $.ajax({
            url: $SCRIPT_ROOT + "/submit_comment",
            data: JSON.stringify({ name: uname, comment: comment, post_id: post_id }),
            method: "POST",
            datatype: 'json',
            contentType: "application/json; charset=utf-8"
        })
        .done(function(data, status ) {
            addElement(data);
            tinyMCE.activeEditor.setContent('');
            $('#inputId').val('');
            no_of_comments = $('#tc-comments').text();
            no_of_comments = Number(no_of_comments) + 1;
            $('#tc-comments').text(no_of_comments);
        }).fail(function(data, status) {
        });
    });
});

$(function() { 
    $('#submitWithOutName').click(function() {
        var comment = $('textarea[name="comment"]').val();
        var no_of_comments;

        if (comment == '') {
            alert("Name and Comment should not be empty");
            return;
        }        

        $.ajax({
            url: $SCRIPT_ROOT + "/submit_comment",
            data: JSON.stringify({ comment: comment, post_id: post_id }),
            method: "POST",
            datatype: 'json',
            contentType: "application/json; charset=utf-8"
        })
        .done(function(data, status ) {  
            alert('got reply');          
            addElement(data);
            $('#inputId').val('');
            tinyMCE.activeEditor.setContent('');
            no_of_comments = Number(no_of_comments) + 1;
            $('#tc-comments').text(no_of_comments);                        
        }).fail(function(data, status) {
        });
    });
});

//$(document).ready(function(){
//    console.log("postPic");
//    $("#postPic").attr("src", post_pic_url);
//    $('#postPic').width(1200);
//    $('#postPic').height(550);
//})

$(document).ready(function(){
    $("#zonePic").attr("src", 'football_zones.png');
})

$(function() {
    $('#fbId').width(200);
    $('#fbId').height(25);
});

$(function() {
    $('#twId').width(200);
    $('#twId').height(25);
});

function withoutUsercheck() {
    var txtvalue=$.trim($("#textIdwithOutUser").val());
    var nameValue=$.trim($("#inputId").val());
    if(txtValue > 0 && nameValue > 0) {
      $("#submitWithName").prop('disabled', false);
    } else {
      $("#submitWithName").prop('disabled', true);
    }
}

function withUsercheck() {
    var txtvalue=$.trim($("#textIdwithUser").val());
    if(txtValue > 0) {
      $("#submitWithOutName").prop('disabled', false);
    } else {
      $("#submitWithOutName").prop('disabled', true);
    }
}

function tw_click(twttr, post_url, post_header, post_tag) {
    var twtTitle = document.title;
    var twtUrl = post_url;
    var dataSize = "large";
    var dataText=post_header;
    var dataHashtags = "football, football_tactics," + post_tag;
    var dataVia = "tactification1"
    var maxLength = 140 - (twtUrl.length + 1);
    if (twtTitle.length > maxLength) {
        twtTitle = twtTitle.substr(0, (maxLength - 3)) + '...';
    }

    
    var twtLink = 'http://twitter.com/share?url=' + encodeURIComponent(twtUrl) + "&text=" + encodeURIComponent(dataText) +  "&hashtags=" + encodeURIComponent(dataHashtags) + "&via=" +encodeURIComponent(dataVia);
    window.open(twtLink, "toolbar=yes,scrollbars=yes,resizable=yes,top=300,left=500,width=700,height=400");
    //<a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-show-count="false">Tweet</a><script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>
    //<a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" data-text="Football is my religion" data-via="deepakpjose" data-hashtags="football" data-show-count="false">Tweet</a><script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script-->
}

function fb_click(post_url, post_header, post_pic_url) {  
    //var facebookShrLink = 'https://www.facebook.com/dialog/share?app_id=613455148848789&display=popup&href=' + encodeURIComponent(post_url) + '&redirect_uri=' + encodeURIComponent(post_url);
    FB.ui({
        method: 'share',
        mobile_iframe: true,
        href: post_url,
        quote: post_header
      }, function(response){});
    //window.open(facebookShrLink);
}

$(document).ready(function(){
    $("#myModal").on("shown.bs.modal",function(){
       $('#myModal').removeClass('in');
    })
})

function PlayVideo(vId, isEmbedded) {
    var iframe=document.getElementById("iframeYoutube");
    if (isEmbedded == 0) {
        window.open("https://youtu.be/"+vId);
    } else {
        iframe.src="https://www.youtube.com/embed/"+vId;
        $("#myModal").modal("show");
    }
}

$("#myModal").on('hidden.bs.modal', function (e) {
    $("#myModal iframe").attr("src", $("#myModal iframe").attr("src"));
});

function yt_click(post_id){
    $.ajax({
        url: $SCRIPT_ROOT + "/play_video",
        data: JSON.stringify({ post_id: post_id }),
        method: "POST",
        datatype: 'json',
        contentType: "application/json; charset=utf-8"
    })
    .done(function(data, status ) {
        if (data['result'] == 'pass')
            if (data['display'] == true) {
                PlayVideo(data['video_id'], data['is_embedded']);
            } else {
                alert('Video will be uploaded in ' + moment(data['date']).fromNow());     
            }                       
    }).fail(function(data, status) {
    });
}

function test_field(is_authenticated) {
    if (is_authenticated == true) {
        if(document.getElementById("textIdwithUser").value == '') {
            alert("No comments");
        }        
    } else {
        if ((document.getElementById("inputId").value == '') ||
            (document.getElementById("textIdwithOutUser").value == '')) {
            alert("Name and Comment should not be empty");
        }
    }
}

function updateStatusCallback(response) {
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
    } else {
      // The person is not logged into your app or we are unable to tell.
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
      //FB.getLoginStatus(updateStatusCallback);
    });
});