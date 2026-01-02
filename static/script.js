const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const menuBtn = document.getElementById("menuBtn");
const menuBox = document.getElementById("menuBox");

/* MENU */
menuBtn.onclick = () => {
  menuBox.style.display = menuBox.style.display === "block" ? "none" : "block";
};

/* SAVE HISTORY */
function save(role, text){
  let h = JSON.parse(localStorage.getItem("gpchat")) || [];
  h.push({role,text});
  localStorage.setItem("gpchat", JSON.stringify(h));
}

/* LOAD HISTORY */
window.onload = () => {
  let h = JSON.parse(localStorage.getItem("gpchat")) || [];
  h.forEach(m => addMsg(m.role, m.text));
};

function addMsg(role, text){
  const div = document.createElement("div");
  div.className = "bubble " + role;
  div.innerText = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

/* SEND */
async function sendMsg(text=null){
  const msg = text || input.value.trim();
  if(!msg) return;

  addMsg("user", msg);
  save("user", msg);
  input.value = "";

  try{
    const res = await fetch("/chat",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:msg})
    });
    const data = await res.json();
    addMsg("GP", data.reply);
    save("GP", data.reply);
  }catch{
    addMsg("GP","❌ Server error");
  }
}

/* HISTORY VIEW */
function openHistory(){
  let h = JSON.parse(localStorage.getItem("gpchat")) || [];
  alert(h.map(x=>`${x.role}: ${x.text}`).join("\n\n") || "No history");
}

/* CLEAR */
function clearHistory(){
  if(confirm("Clear chat history?")){
    localStorage.removeItem("gpchat");
    location.reload();
  }
}

input.addEventListener("keydown",e=>{
  if(e.key==="Enter") sendMsg();
});
