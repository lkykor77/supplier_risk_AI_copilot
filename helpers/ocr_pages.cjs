const fs = require('node:fs/promises');
const path = require('node:path');
const {createWorker} = require('tesseract.js');
(async()=>{
  const [directory, languageDirectory, cacheDirectory] = process.argv.slice(2);
  const files=(await fs.readdir(directory)).filter(file=>/^page-\d+\.png$/.test(file)).sort((a,b)=>Number(a.match(/\d+/)[0])-Number(b.match(/\d+/)[0]));
  const worker=await createWorker('eng+kor',1,{langPath:languageDirectory,cachePath:cacheDirectory,gzip:true});
  try{
    const pages=[];
    for(const file of files){const result=await worker.recognize(path.join(directory,file));pages.push({page:Number(file.match(/\d+/)[0]),text:result.data.text.trim(),confidence:result.data.confidence/100});}
    process.stdout.write(JSON.stringify({pages}));
  }finally{await worker.terminate();}
})().catch(()=>{process.stderr.write('Local Tesseract OCR failed. Check OCR setup and language files.');process.exit(1);});
