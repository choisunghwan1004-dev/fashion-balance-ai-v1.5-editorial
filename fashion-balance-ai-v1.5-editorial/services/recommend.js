const db=require('../db');
const coreCategories=['아우터','상의','하의','신발'];
const optionalCategories=['모자','스카프','가방','벨트','시계','주얼리'];
const neutrals=new Set(['베이지','화이트','네이비','브라운','블랙','그레이']);
function purchasePrice(item){return item.is_owned?0:Number(item.price)}
function evaluate(items,trend){
 const colors=new Set(items.map(i=>i.color_name));const allNeutral=items.every(i=>neutrals.has(i.color_name));
 const colorScore=Math.max(8,25-Math.max(0,colors.size-3)*5-(allNeutral?0:4));
 const ownedCount=items.filter(i=>i.is_owned).length;
 return Math.min(100,colorScore+20+20+Math.round(trend*.15)+10+10+Math.min(5,ownedCount));
}
function buildOutfit(items,trend){const total_purchase=items.reduce((sum,i)=>sum+purchasePrice(i),0);const owned=items.filter(i=>i.is_owned);const buy=items.filter(i=>!i.is_owned);return {items:items.map(i=>({...i,purchase_price:purchasePrice(i),source:i.is_owned?'wardrobe':'shop'})),purchase_total:total_purchase,total_price:total_purchase,owned_count:owned.length,shopping_count:buy.length,shopping_items:buy.map(i=>i.id),balance_score:evaluate(items,trend),trend_score:trend};}
async function recommend({season,style,budget,source='mixed',anchorCategory=null,anchorColor=null}){
 const [rows]=await db.execute(`SELECT i.id,i.name,i.price,i.image_url,i.shop_url,i.owner_user_id,c.name category_name,co.name color_name,
 CASE WHEN w.item_id IS NOT NULL THEN 1 ELSE 0 END AS is_owned
 FROM fashion_items i JOIN categories c ON c.id=i.category_id JOIN colors co ON co.id=i.color_id JOIN styles s ON s.id=i.style_id
 LEFT JOIN wardrobe_items w ON w.item_id=i.id AND w.user_id=1
 WHERE i.active=1 AND (i.owner_user_id IS NULL OR i.owner_user_id=1)
 AND (i.season=? OR i.season='사계절') AND s.name=?
 ORDER BY is_owned DESC,i.price ASC,i.id ASC LIMIT 500`,[season,style]);
 const filtered=rows.filter(i=>source==='wardrobe'?!!i.is_owned:source==='shop'?!i.is_owned:true);
 // 선택한 바지/아우터 색상과 일치하는 상품을 반드시 포함한다.
 if(anchorCategory && !filtered.some(i=>i.category_name===anchorCategory && i.color_name===anchorColor))return [];
 const anchored=anchorCategory?filtered.filter(i=>i.category_name===anchorCategory&&i.color_name===anchorColor):[];
 const groups=Object.fromEntries([...coreCategories,...optionalCategories].map(c=>[c,filtered.filter(i=>i.category_name===c)]));
 if(coreCategories.some(c=>!groups[c].length))return [];
 const [trends]=await db.execute('SELECT t.score FROM trends t JOIN styles s ON s.id=t.style_id WHERE t.season=? AND s.name=? ORDER BY t.year DESC,t.id DESC LIMIT 1',[season,style]);const trend=trends.length?Number(trends[0].score):50;
 // 먼저 보유 의류, 그 다음 저렴한 쇼핑 상품. 최대 4^4 조합만 평가
 const sort=(a,b)=>Number(b.is_owned)-Number(a.is_owned)||purchasePrice(a)-purchasePrice(b);
 const selections=coreCategories.map(c=>(c===anchorCategory?anchored:groups[c]).sort(sort).slice(0,4));const candidates=[];
 for(const a of selections[0])for(const b of selections[1])for(const c of selections[2])for(const d of selections[3]){
  const core=[a,b,c,d];let total=core.reduce((s,i)=>s+purchasePrice(i),0);if(total>budget)continue;
  const extras=[];
  // 선택적 액세서리는 보유품 우선. 구매가 필요한 경우 가방 1개까지만 자동 보완.
  for(const category of optionalCategories){const item=groups[category].sort(sort).find(i=>i.is_owned || (category==='가방' && total+purchasePrice(i)<=budget));if(item){extras.push(item);total+=purchasePrice(item)}}
  const outfit=buildOutfit([...core,...extras],trend);candidates.push(outfit);
 }
 // 동일 아이템 조합 중복 제거, 보유 수 우선 + 점수 + 쇼핑 비용
 const unique=[...new Map(candidates.map(x=>[x.items.map(i=>i.id).join('-'),x])).values()];
 const ranked=unique.sort((a,b)=>b.owned_count-a.owned_count||b.balance_score-a.balance_score||a.purchase_total-b.purchase_total);
 // 같은 코디를 반복 표시하지 않도록 가능한 경우 서로 다른 핵심 아이템을 선택
 const selected=[];const signatures=new Set();for(const o of ranked){const signature=o.items.filter(i=>coreCategories.includes(i.category_name)).map(i=>i.id).join('-');if(!signatures.has(signature)){selected.push(o);signatures.add(signature)}if(selected.length===2)break;}return selected;
}
module.exports={recommend,buildOutfit,purchasePrice};
