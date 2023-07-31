function SetCover(){
    const cover_input = document.getElementById('cover_input');
    cover_input.click();
}

function GetCover(event){
    const cover_img = document.getElementById('cover_img');
    const files = event.target.files;
    const file = files[0];

    const reader = new window.FileReader();
    reader.readAsDataURL(file);
    reader.addEventListener('load', function(){
        const result = reader.result;
        cover_img.src = result;
    })
}

function SetCategory(name){
    const category_input = document.getElementById('category_input');
    category_input.value = name;
}

function SetTag(name){
    const tag_input = document.getElementById('tag_input');
    var value = tag_input.value;
    if (value){
        if (!(value.includes(name))){
            value = value + " " + name;
        }
    }
    else{
        value = name;
    }
    tag_input.value = value;
}

function SetStatus(){
    const status_input = document.getElementById("status_input");
    status_input.value = "1";
}