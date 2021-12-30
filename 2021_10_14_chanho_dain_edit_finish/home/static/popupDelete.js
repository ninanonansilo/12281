function showPopupDelete(hasFilter) {
	const popup = document.querySelector('#popupDelete');
  
  if (hasFilter) {
  	popup.classList.add('has-filter');
  } else {
  	popup.classList.remove('has-filter');
  }
  
  popup.classList.remove('hide');
}

function closePopupDelete() {
	const popup = document.querySelector('#popupDelete');
  popup.classList.add('hide');
}
