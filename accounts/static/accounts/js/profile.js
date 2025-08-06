  function showTab(index) {
      const buttons = document.querySelectorAll('.profile__tab-button');
      const contents = document.querySelectorAll('.profile__tab-content');

      buttons.forEach(btn => btn.classList.remove('profile__tab-button--active'));
      contents.forEach(tab => tab.classList.remove('profile__tab-content--active'));

      
      contents[index].classList.add('profile__tab-content--active');
    }