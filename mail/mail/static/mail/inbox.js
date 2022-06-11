document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', submit_email);

  

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector("#email-view").style.display = "none";

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}



function submit_email(event) {
  event.preventDefault();
  
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients: document.querySelector("#compose-recipients").value,
      subject: document.querySelector("#compose-subject").value,
      body: document.querySelector("#compose-body").value
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    load_mailbox("sent");
  })
  

}






function load_email(id) {
  fetch("/emails/" + id)
    .then(response => response.json())
    .then(email => {
      document.querySelector("#emails-view").style.display = "none";
      document.querySelector("#compose-view").style.display = "none";
      document.querySelector("#email-view").style.display = "block";

      const view = document.querySelector("#email-view");
      view.innerHTML = `
        <ul class="list-group">
          <li class="list-group-item"><b>From:    </b> <span>${email["sender"]}</span></li>
          <li class="list-group-item"><b>To:      </b> <span>${email["recipients"]}</span></li>
          <li class="list-group-item"><b>Subject: </b> <span>${email["subject"]}</span></li>
          <li class="list-group-item"><b>Time:    </b> <span>${email["timestamp"]}</span></li>
        </ul>
        <p class="m-2"><b>${email["body"]}</b></p>
      `    


      // Create "mark as unread" button and append it to DOM
      readButton = document.createElement("button");
      readButton.className = ("btn-secondary m-1");
      readButton.innerHTML = "Mark as Unread";
      readButton.addEventListener("click", function() {
        fetch("/emails/" + email["id"], {
          method: "PUT",
          body: JSON.stringify({
            read: false
          })
        })
        .then(response => load_mailbox("inbox"))
      })
      view.appendChild(readButton);

      // Mark this email as read
      if(!email["read"]) {
        fetch("/emails/" + email["id"], {
          method: "PUT",
          body: JSON.stringify({
            read: true
          })
        })
      }
    }) 


  
  
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector("#email-view").style.display = "none";

  // Show the mailbox name
  const view = document.querySelector('#emails-view');
  view.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch("/emails/" + mailbox)
    .then(response => response.json())
    // .then(emails => console.log(emails))

    .then(emails => {

      // Generate div for each mail
      emails.forEach(email => {
        let div = document.createElement("div");
        div.className = email["read"] ? "email-list-item-read" : "email-list-item-unread";
        div.innerHTML = `
          <span class="sender col-3"><b>${email["sender"]}</b></span>
          <span class="subject col-6"><b>${email["subject"]}</b></span>
          <span class="timestamp col-3"><b>${email["timestamp"]}</b></span>
        `;
        div.addEventListener("click", () => load_email(email["id"]));
        view.appendChild(div);
      });
    })

  
}