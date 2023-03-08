const usernameField = document.querySelector('#usernameField')
const feedbackUserField = document.querySelector('.invalid_username');
const feedbackEmailField = document.querySelector('.invalid_email');
const emailField = document.querySelector('#emailField')
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput')
const showPasswordToggle = document.querySelector('.showPasswordToggle')
const passwordField = document.querySelector('#passwordField')
const submitBtn = document.querySelector('.submit-btn')

const handleToggleInput=(e)=>{
    if (showPasswordToggle.textContent==='SHOW'){
        showPasswordToggle.textContent='HIDE';
        passwordField.setAttribute("type", "text")
    } else {
        showPasswordToggle.textContent='SHOW';
        passwordField.setAttribute("type", "password")
    }


}

showPasswordToggle.addEventListener('click',handleToggleInput);
usernameField.addEventListener('keyup', (e) => {
    const usernameVal = e.target.value;
    usernameSuccessOutput.style.display = 'block'
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`

    usernameField.classList.remove("is-invalid")
    feedbackUserField.style.display = 'none'

    if (usernameVal.length > 0) {
        fetch("http://127.0.0.1:8000/authentication/validate-username/", {
            body: JSON.stringify({username: usernameVal}),
            method: "POST",
        }).then((res) => res.json())
            .then((data) => {
                usernameSuccessOutput.style.display = 'none';
                if (data.username_error) {
                    usernameField.classList.add("is-invalid")
                    feedbackUserField.innerHTML = `<p>${data.username_error}</p>`;
                    feedbackUserField.style.display = 'block';
                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute("disabled");
                }
            });

    }// end if
});//end ael

emailField.addEventListener('keyup', (e) => {
    const emailVal = e.target.value;

    emailField.classList.remove("is-invalid")
    feedbackEmailField.style.display = 'none'

    if (emailVal.length > 0) {
        fetch('http://127.0.0.1:8000/authentication/validate-email/',
            {
                body: JSON.stringify({email: emailVal}),
                method: "POST"
            }).then((res) => res.json())
            .then((data) => {
                if (data.email_error) {
                    emailField.classList.add('is-invalid');
                    feedbackEmailField.innerHTML = `<p>${data.email_error}</p>`;
                    feedbackEmailField.style.display = 'block';
                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute("disabled")
                }
            })
    }
})
