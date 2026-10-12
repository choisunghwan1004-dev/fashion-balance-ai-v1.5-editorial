const router=require('express').Router();
const db=require('../db');
router.get('/',async(req,res,next)=>{try{
 const season=req.query.season||'가을';
 if(!['봄','여름','가을','겨울'].includes(season))return res.status(400).json({error:'계절 오류'});
 const [rows]=await db.execute('SELECT id,season,look_no,title,description,image_url,style_name,sample_only FROM seasonal_looks WHERE season=? ORDER BY look_no LIMIT 2',[season]);
 res.json(rows);
}catch(e){next(e)}});
module.exports=router;
