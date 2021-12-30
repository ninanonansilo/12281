var submit = document.getElementById('submitButton');
submit.onclick = showImage;     //Submit 버튼 클릭시 이미지 보여주기

function showImage() {
    var newImage = document.getElementById('image-show').lastElementChild;
    newImage.style.visibility = "visible";
    
    document.getElementById('image-upload').style.visibility = 'hidden';

    document.getElementById('fileName').textContent = null;     //기존 파일 이름 지우기
}
/*
function loadFile(input) {
    var file = input.files[0];
    var name = document.getElementById('fileName'); // 파일 이름 받아옴

    name.textContent = file.name;
}; */

/*
function loadFile(input) {
    var file = input.files[0];
    var name = document.getElementById('fileName'); // 파일 이름 받아옴

    name.textContent = file.name;
    $.ajax({
        url : '{% url 'upload_img' %}',
        type : 'POST',
        data : file,
        dataType : 'json',
        processData : false,
        contentType : false,
        success:function(data){
        },
        error: function(){
            alert('error');}
    });

};
*/
