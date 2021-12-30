
function showPopupDelete_text(hasFilter) {
	const popup = document.querySelector('#popupDelete_text');
  
  if (hasFilter) {
  	popup.classList.add('has-filter');
  } else {
  	popup.classList.remove('has-filter');
  }
  
  popup.classList.remove('hide');
}


function closePopupDelete_text() {
	const popup = document.querySelector('#popupDelete_text');
  popup.classList.add('hide');
}