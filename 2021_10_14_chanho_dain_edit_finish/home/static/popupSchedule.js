function showPopups(hasFilter) {
	const popup = document.querySelector('#popups');
  
  if (hasFilter) {
  	popup.classList.add('has-filter');
  } else {
  	popup.classList.remove('has-filter');
  }
  
  popup.classList.remove('hide');
}

function closePopups() {
	const popup = document.querySelector('#popups');
  popup.classList.add('hide');
}




