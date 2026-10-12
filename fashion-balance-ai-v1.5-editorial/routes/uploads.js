const router=require('express').Router();
const fs=require('fs/promises');const path=require('path');const crypto=require('crypto');
const dest=path.join(__dirname,'../public/uploads');
router.post('/',async(req,res,next)=>{try{
 const data=req.body&&req.body.data;
 if(typeof data!=='string'||data.length>4300000)return res.status(400).json({error:'사진은 최대 3MB까지 가능합니다.'});
 const match=/^data:image\/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)$/.exec(data);
 if(!match)return res.status(400).json({error:'JPG, PNG, WEBP 파일만 가능합니다.'});
 const bytes=Buffer.from(match[2],'base64');if(bytes.length>3*1024*1024||bytes.length<16)return res.status(400).json({error:'사진 크기를 확인하세요.'});
 const type=match[1],valid=type==='jpeg'?bytes.subarray(0,3).equals(Buffer.from([255,216,255])):type==='png'?bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])):bytes.toString('ascii',0,4)==='RIFF'&&bytes.toString('ascii',8,12)==='WEBP';
 if(!valid)return res.status(400).json({error:'사진 파일 형식이 올바르지 않습니다.'});
 await fs.mkdir(dest,{recursive:true});const file=crypto.randomUUID()+'.'+(type==='jpeg'?'jpg':type);await fs.writeFile(path.join(dest,file),bytes,{flag:'wx'});res.status(201).json({image_url:'/uploads/'+file,recognition:false});
 }catch(e){next(e)}});module.exports=router;
