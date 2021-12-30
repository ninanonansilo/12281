
function showPopupletter(hasFilter) {
	const popup = document.querySelector('#popupletter');
  
  if (hasFilter) {
  	popup.classList.add('has-filter');
  } else {
  	popup.classList.remove('has-filter');
  }
  
  popup.classList.remove('hide');
}


function closePopupletter() {
	const popup = document.querySelector('#popupletter');
  popup.classList.add('hide');
}