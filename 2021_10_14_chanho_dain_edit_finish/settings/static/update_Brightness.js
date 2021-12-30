
let btnAjax = document.getElementById('brigtness_button');
btnAjax.addEventListener('click', e => {
    let input = document.getElementById('input_brigtness').value;
    let param ={'input':input, }

    $.ajax({
        url : '{% url 'update_Brightness' %}',
        type : 'POST',
        data : param,
        success:function(data){
                            },
        error: function(){
            alert('error');}
        });
});
