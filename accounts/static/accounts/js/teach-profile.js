function showCoachTab(index) {
  const buttons = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.coach-tab-content');

  console.log('Buttons count:', buttons.length);
  console.log('Contents count:', contents.length);
  console.log('Requested index:', index);

  buttons.forEach(btn => btn.classList.remove('active'));
  contents.forEach(tab => tab.classList.remove('active'));

  if(buttons[index] && contents[index]) {
    buttons[index].classList.add('active');
    contents[index].classList.add('active');
  } else {
    console.warn('Tab or content at index', index, 'does not exist!');
  }
}
