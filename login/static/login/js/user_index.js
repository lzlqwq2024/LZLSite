tinymce.init({
    selector: '#editor-space',
    plugins: 'lists, advlist, anchor, autolink, autosave, charmap, emoticons, fullscreen, link, preview, table, searchreplace, image',
    toolbar: 'undo redo restoredraft  searchreplace| preview | newdocument fullscreen | cut copy paste | lineheight hr | bold italic underline strikethrough subscript superscript forecolor backcolor blockquote | alignleft aligncenter alignright alignjustify | styleselect formatselect fontselect fontsizeselect removeformat | outdent indent | bullist numlist table | anchor link | charmap emoticons image',
    auto_focus: true,
    branding: false,
    elementpath: false,
    promotion: false,
    height: 500,
    placeholder: '在此处输入内容…',
    language: "zh-Hans",
    images_upload_url: '/login/upload_image/',
});

function turn_editor_visible(){
    document.getElementById('editor-wrapper').removeAttribute("style");
    document.getElementById('user-detail-group').style.display = "none";
}

function turn_text_visible(){
    document.getElementById('user-detail-group').removeAttribute("style");
    document.getElementById('editor-wrapper').style.display = "none";
}

function getImg(){
    document.querySelector('#avatar-upload').click();
}

function uploadImg(){
    document.querySelector('#avatar-form').submit();
}

function uploadDescription(){
    document.querySelector('#description-form').submit();
}

var avatar_div = document.getElementById('avatardiv');
var timer = null;
var alpha = 100;
var speed = 1.5;
var avatar_type = 0;
function avatar_mouseover(){
    startChange(avatar_div,speed,30);
}
function avatar_mouseout(){
    startChange(avatar_div,speed,30);
}

function show_SmallDescriptionModal(){
    $('#description-modal').modal('show');
}

function logout(){
    swal({
        title: "确定要登出吗？",
        icon: "warning",
        closeOnClickOutside: true,
        buttons: ['取消', '确定']
    }).then((willLogout) => {
        if (willLogout){
            window.location.href = '/login/logout/';
        }
    });
}

function reset_password(){
    swal({
        title: "确定要修改密码吗？",
        icon: "warning",
        closeOnClickOutside: true,
        buttons: ['取消', '确定']
    }).then((willReset) => {
        if (willReset){
            window.location.href = '/login/reset/';
        }
    });
}

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});