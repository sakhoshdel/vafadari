
// document.getElementById("referralCode").addEventListener("click", function() {
//     // Get the referral code
//     var referralCode = document.getElementById("referralCode").textContent;

//     // Create a temporary input element
//     var input = document.createElement("input");
//     input.setAttribute("value", referralCode);
//     document.body.appendChild(input);

//     // Select and copy the text inside the input element
//     input.select();
//     document.execCommand("copy");

//     // Remove the temporary input element
//     document.body.removeChild(input);

//     // Provide user feedback
//     alert("Referral code copied to clipboard: " + referralCode);

//     // Redirect the user to the registration page with the referral code as a query parameter
//     window.location.href = "/register?ref=" + referralCode;
// });


// document.getElementById("affliate-link-btn").addEventListener("click", function() {
//     // Get the referral code
//     var referralCode = document.getElementById("referralCode").textContent;
//     var referralCode = 'https://vafadar.dalgaweb.ir/register?ref=' + referralCode

//     // Create a temporary input element
//     var input = document.createElement("input");    
//     input.setAttribute("value", referralCode);
//     document.body.appendChild(input);

//     // Select and copy the text inside the input element
//     input.select();
//     document.execCommand("copy");

//     // Remove the temporary input element
//     document.body.removeChild(input);

//     // Show the copy message
//     var copyMessage = document.getElementById("copyMessage");
//     copyMessage.style.display = "block";

//     // Hide the copy message after 1 second
//     setTimeout(function() {
//         copyMessage.style.display = "none";
//     }, 1000);
// });

// document.getElementById("referralCodeValue").textContent = "{{ user.referral_code }}";

    // document.getElementById("referralLink").addEventListener("click", function(e) {
    //     e.preventDefault(); // Prevent the link from navigating

    //     var referralCode = "{{ user.referral_code }}";

    //     // Create a temporary input element
    //     var input = document.createElement("input");
    //     input.setAttribute("value", referralCode);
    //     document.body.appendChild(input);

    //     // Select and copy the text inside the input element
    //     input.select();
    //     document.execCommand("copy");

    //     // Remove the temporary input element
    //     document.body.removeChild(input);

    //     // Show the copy message
    //     var copyMessage = document.getElementById("copyMessage");
    //     copyMessage.classList.add("show");

    //     // Hide the copy message after 1 second
    //     setTimeout(function() {
    //         copyMessage.classList.remove("show");
    //     }, 1000);
    // });


const referralLinkBtn = document.getElementById("affliate-link-btn")
if(referralLinkBtn){
    referralLinkBtn.addEventListener("click", function () {
    // Get the referral code
    var referralCode = this.getAttribute("data-referral-code");
    var referralLink = referralCode;

    // Create a temporary input element
    var input = document.createElement("input");
    input.setAttribute("value", referralLink);
    document.body.appendChild(input);

    // Select and copy the text inside the input element
    input.select();
    document.execCommand("copy");

    // Remove the temporary input element
    document.body.removeChild(input);

    // Show the tooltip with "کپی کد معرفی"
    var affliatelinkbtn = document.getElementById("affliate-link-btn");
    var tooltip = new bootstrap.Tooltip(affliatelinkbtn, { boundary: document.body });
    tooltip.show();
    setTimeout(function () {
        tooltip.hide();
    }, 2000);
    });

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
    })
}