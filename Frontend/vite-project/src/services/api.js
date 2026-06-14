export const streamResponse = async(query,onChunk)=>{
    const response = await  fetch("http://127.0.0.1:8000/ai_call/",{
        method:"POST",
        headers:{
              "Content-Type": "application/x-www-form-urlencoded",
        },
        body :new URLSearchParams ({
            query 
        })
    })
    const reader = response.body.getReader()
    const decoder = new TextDecoder();
    let result ="";
    while(true){
        const{value,done}= await reader.read();
        if(done) break;
        result+=decoder.decode(value);
        onChunk(result);
    }

};