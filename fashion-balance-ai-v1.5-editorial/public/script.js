const form=document.querySelector('#recommendForm'),results=document.querySelector('#results');
const categorySelect=document.querySelector('#anchorCategory'),colorSelect=document.querySelector('#anchorColor');
async function loadAnchorColors(){const category=categorySelect.value;colorSelect.replaceChildren();if(!category){colorSelect.disabled=true;colorSelect.append(new Option('먼저 기준 아이템을 선택하세요',''));return;}colorSelect.disabled=false;colorSelect.append(new Option('색상을 선택하세요',''));try{const r=await fetch('/api/outfits/anchor-colors?category='+encodeURIComponent(category));if(!r.ok)throw Error('색상 조회 실패');const colors=await r.json();colors.forEach(c=>colorSelect.append(new Option(c,c)));if(!colors.length)colorSelect.replaceChildren(new Option('등록된 색상이 없습니다',''));}catch(e){colorSelect.replaceChildren(new Option('색상 조회 오류',''));}}
categorySelect.addEventListener('change',loadAnchorColors);
let selectedLook=null;
const won=n=>Number(n).toLocaleString('ko-KR')+'원';
function el(tag,text,cls){const x=document.createElement(tag);if(text!==undefined)x.textContent=text;if(cls)x.className=cls;return x}
form.addEventListener('submit',async e=>{e.preventDefault();results.replaceChildren(el('p','나만의 코디를 찾고 있습니다…','muted'));try{
const body={season:document.querySelector('#season').value,style:document.querySelector('#style').value,budget:Number(document.querySelector('#budget').value),source:document.querySelector('#source').value,anchorCategory:categorySelect.value||null,anchorColor:colorSelect.value||null};if(body.anchorCategory&&!body.anchorColor){results.replaceChildren(el('p','기준 색상을 먼저 선택하세요.','empty'));return;}
document.querySelector('#acceptedStatus').textContent='새 추천을 조회했습니다. 코디를 선택해 주세요.';const r=await fetch('/api/outfits/recommend',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await r.json();if(!r.ok)throw Error(data.error||'추천 요청 실패');results.replaceChildren();const notice=el('div',`✓ 적용된 조건: ${body.season} / ${body.style} / ${body.anchorCategory?body.anchorColor+' '+body.anchorCategory:'기준 옷 자동'} / ${body.source==='mixed'?'내 옷 우선':body.source==='wardrobe'?'내 옷만':'쇼핑만'} / 예산 ${won(body.budget)}`,'applied-notice');results.append(notice);if(!data.length){results.append(el('div','선택한 색상의 바지/겉옷을 포함하는 코디가 없습니다. 해당 색상의 의류를 등록하거나 계절·스타일·예산을 변경하세요. 내 옷장에 아우터·상의·하의·신발을 등록하거나 예산과 스타일을 변경해 보세요.','empty'));return}
data.forEach((outfit,n)=>{const card=el('article',undefined,'outfit');card.dataset.look=String(n+1);const top=el('div',undefined,'outfit-head');const h=el('div');h.append(el('span',`LOOK 0${n+1}`,'eyebrow'),el('h2',`추천 코디 ${n+1}${body.anchorCategory?' · '+body.anchorColor+' '+body.anchorCategory:''}`));top.append(h,el('span',`밸런스 ${outfit.balance_score}점`,'score'));card.append(top);
const stats=el('div',undefined,'stats');[['내 옷 활용',outfit.owned_count+'개'],['추가 구매',outfit.shopping_count+'개'],['추가 구매 합계',won(outfit.purchase_total)]].forEach(([k,v])=>{const box=el('div',undefined,'stat');box.append(el('span',k),el('strong',v));stats.append(box)});card.append(stats);
const grid=el('div',undefined,'items');outfit.items.forEach(item=>{const box=el('div',undefined,'item');if(item.image_url){const pic=el('img');pic.src=item.image_url;pic.alt=item.name;pic.loading='lazy';pic.className='item-photo';box.append(pic)}box.append(el('span',item.source==='wardrobe'?'내 옷 · 0원':'쇼핑 추천','item-badge '+(item.source==='wardrobe'?'owned':'shopping')),el('span',item.category_name,'eyebrow'),el('strong',item.name),el('span',item.color_name+' · '+won(item.purchase_price),'item-price'));if(item.source==='shop'&&item.shop_url){const a=el('a','쇼핑몰에서 검색 ↗');a.href=item.shop_url;a.target='_blank';a.rel='noopener noreferrer';box.append(a)}else if(item.source==='shop'){box.append(el('small','구매 링크 미등록','muted'))}grid.append(box)});card.append(grid);const choose=el('button','이 코디 채택하기 ✓','choose-look');choose.type='button';choose.addEventListener('click',()=>{document.querySelectorAll('.outfit').forEach(x=>x.classList.remove('accepted'));card.classList.add('accepted');selectedLook=n+1;document.querySelector('#acceptedStatus').textContent=`✓ LOOK ${n+1} 채택 완료 · 보유 의류 ${outfit.owned_count}개 · 추가 구매 ${won(outfit.purchase_total)} (화면 테스트용 선택, DB 저장 없음)`;document.querySelector('#acceptedStatus').scrollIntoView({block:'nearest',behavior:'smooth'});});card.append(choose);results.append(card)})}catch(err){results.replaceChildren(el('p','오류: '+err.message,'empty'))}});

// DB에 등록한 계절별 LOOK 2개 표시
const lookGrid=document.querySelector('#seasonalLooks');
async function loadSeasonalLooks(){
 if(!lookGrid)return;
 const season=document.querySelector('#season').value;
 lookGrid.replaceChildren(el('p','계절별 샘플 사진을 불러오는 중…','muted'));
 try{
  const response=await fetch('/api/seasonal-looks?season='+encodeURIComponent(season));
  if(!response.ok)throw Error('계절 샘플을 불러올 수 없습니다.');
  const looks=await response.json();lookGrid.replaceChildren();
  looks.forEach(look=>{
   const card=el('article',undefined,'look-card');
   const photo=el('img');photo.src=look.image_url;photo.alt=look.title+' 참고용 코디 이미지';photo.loading='lazy';
   const details=el('div',undefined,'look-details');
   details.append(el('span',season+' · LOOK '+look.look_no,'eyebrow'),el('h3',look.title),el('p',look.description,'muted'),el('span',look.style_name+' · 샘플 이미지','soft-label'));
   card.append(photo,details);lookGrid.append(card);
  });
 }catch(e){lookGrid.replaceChildren(el('p','샘플을 불러오지 못했습니다. upgrade_v1_2.sql 실행 여부를 확인하세요.','empty'))}
}
document.querySelector('#season').addEventListener('change',()=>{loadSeasonalLooks();const x=document.querySelector('#acceptedStatus');if(x)x.textContent='아직 선택한 코디가 없습니다.';});
loadSeasonalLooks();
