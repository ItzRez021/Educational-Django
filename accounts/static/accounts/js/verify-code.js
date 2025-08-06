document.querySelectorAll('.verify__inputs input').forEach((input, index, all) => {
  input.addEventListener('input', () => {
    if (input.value.length === 1 && all[index + 1]) {
      all[index + 1].focus();
    }
  });
});

