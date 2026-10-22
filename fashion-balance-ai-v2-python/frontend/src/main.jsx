import React, {useEffect,useState,useRef} from 'react';
import {createRoot} from 'react-dom/client';
import parse,{domToReact,attributesToProps} from 'html-react-parser';
import '@fontsource/noto-sans-kr/korean-400.css';
import '@fontsource/noto-sans-kr/latin-400.css';
import '@fontsource/noto-sans-kr/korean-600.css';
import '@fontsource/noto-sans-kr/latin-600.css';
import './style.css';
import Mobile from './Mobile.jsx';
const sources=import.meta.glob('./templates/*.html',{query:'?raw',import:'default',eager:true});
const page=location.pathname==='/'?'index.html':location.pathname.split('/').pop();
const won=n=>Number(n).toLocaleString('ko-KR')+'원';
const categoryMap={'모자':1,'스카프':2,'아우터':3,'상의':4,'하의':5,'신발':6,'가방':7,'벨트':8,'시계':9,'주얼리':10};
const colorMap={'베이지':1,'화이트':2,'네이비':3,'브라운':4,'블랙':5,'그레이':6};
const initialProfile={face_shape:'미선택',body_shape:'미선택',undertone:'미선택',preferred_fit:'편안한핏'};
const initialGarment={name:'',category_id:'1',color_id:'1',style_id:'1',season:'봄'};
async function api(path,{method='GET',body,protect=false}={}){
 const r=await fetch('/api/'+path,{method,credentials:'same-origin',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});
 const data=await r.json();if(!r.ok){if(r.status===401&&protect)location.assign('/login.html');throw Error(data.error||'요청 실패');}return data;
}
function Template({name,transform}){
 const options={replace(node,index){if(node.type!=='tag')return;if(node.name==='script')return <React.Fragment key={index}/>;
 const props=attributesToProps(node.attribs||{});const change=transform(node,props)||{};const {children,...extra}=change;
 if(change.skip)return <React.Fragment key={index}/>;
 return React.createElement(node.name,{...props,...extra,key:index},...(['input','img','br','hr','meta','link'].includes(node.name)?[]:[children!==undefined?children:domToReact(node.children||[],options)]));}};
 return parse(sources['./templates/'+name]||sources['./templates/index.html'],options);
}
function formOf(node){for(let x=node.parent;x;x=x.parent)if(x.name==='form')return x.attribs?.id;return '';}
function Stats({outfit}){return <div className="stats">{[['내 옷 활용',outfit.owned_count+'개'],['추가 구매',outfit.shopping_count+'개'],['추가 구매 합계',won(outfit.purchase_total)]].map(([label,value])=><div className="stat" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>}
function Outfit({outfit,index,accepted,onChoose,anchor}){return <article className={'outfit'+(accepted?' accepted':'')}><div className="outfit-head"><div><span className="eyebrow">LOOK 0{index+1}</span><h2>추천 코디 {index+1}{anchor?' · '+anchor:''}</h2></div><span className="score">밸런스 {outfit.balance_score}점</span></div><Stats outfit={outfit}/><p className="muted">개인 맞춤: {outfit.personalization?.join(' · ')}</p><div className="items">{outfit.items.map(item=><div className="item" key={item.id}>{item.image_url&&<img className="item-photo" src={item.image_url} alt={item.name} loading="lazy"/>}<span className={'item-badge '+(item.source==='wardrobe'?'owned':'shopping')}>{item.source==='wardrobe'?'내 옷 · 0원':'쇼핑 추천'}</span><span className="eyebrow">{item.category_name}</span><strong>{item.name}</strong><span className="item-price">{item.color_name} · {won(item.purchase_price)}</span>{item.source==='shop'&&(item.shop_url?<a href={item.shop_url} target="_blank" rel="noopener noreferrer">쇼핑몰에서 검색 ↗</a>:<small className="muted">구매 링크 미등록</small>)}</div>)}</div><button type="button" className="choose-look" onClick={onChoose}>이 코디 채택하기 ✓</button></article>}
function Account({user,logout}){return <div className="account-area"><a href="/mobile.html">휴대폰 연결</a>{user?<><span>{user.nickname||'회원'}</span><a href="/history.html">코디 이력</a><button type="button" onClick={logout}>로그아웃</button></>:<a href="/login.html">QR 간편가입 · 로그인</a>}</div>}
async function readPhoto(file){if(!file)return null;if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>3*1024*1024)throw Error('JPG/PNG/WEBP 3MB 이하 사진을 선택하세요.');return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve({file,data:reader.result});reader.onerror=()=>reject(Error('사진 읽기 실패'));reader.readAsDataURL(file);});}
async function localColor(file){const bitmap=await createImageBitmap(file),canvas=document.createElement('canvas');canvas.width=canvas.height=64;const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.drawImage(bitmap,0,0,64,64);bitmap.close();const pixels=ctx.getImageData(0,0,64,64).data;const palette=[['베이지',[210,190,157]],['화이트',[245,243,237]],['네이비',[40,56,83]],['브라운',[118,83,58]],['블랙',[40,40,40]],['그레이',[148,148,148]]],counts={};for(let y=12;y<52;y+=3)for(let x=12;x<52;x+=3){const k=(y*64+x)*4;if(pixels[k+3]<180)continue;let best='',distance=Infinity;for(const [name,rgb] of palette){const d=rgb.reduce((sum,v,i)=>sum+(pixels[k+i]-v)**2,0);if(d<distance){distance=d;best=name;}}counts[best]=(counts[best]||0)+1;}return Object.keys(counts).sort((a,b)=>counts[b]-counts[a])[0];}
function App(){
 const [online,setOnline]=useState(navigator.onLine);
 useEffect(()=>{const update=()=>setOnline(navigator.onLine);window.addEventListener('online',update);window.addEventListener('offline',update);return()=>{window.removeEventListener('online',update);window.removeEventListener('offline',update);};},[]);
 const [user,setUser]=useState(null),[ready,setReady]=useState(false),[notice,setNotice]=useState(''),[busy,setBusy]=useState(false),[popup,setPopup]=useState('');
 const [finder,setFinder]=useState({season:'가을',style:'스마트 캐주얼',budget:'150000',source:'mixed',anchorCategory:'',anchorColor:''});
 const [colors,setColors]=useState([]),[looks,setLooks]=useState([]),[outfits,setOutfits]=useState(null),[applied,setApplied]=useState(null),[selected,setSelected]=useState(null);
 const [items,setItems]=useState([]),[closet,setCloset]=useState([]),[pick,setPick]=useState(''),[garment,setGarment]=useState(initialGarment),[pattern,setPattern]=useState('무지');
 const [profile,setProfile]=useState(initialProfile),[photos,setPhotos]=useState({}),[consent,setConsent]=useState({garment:false,profile:false}),[analysis,setAnalysis]=useState(''),[trends,setTrends]=useState([]),[history,setHistory]=useState([]);
 const [token]=useState(()=>new URLSearchParams(location.hash.slice(1)).get('token'));
 const photoSequence=useRef({});
 const protectedPage=['wardrobe.html','profile.html','admin.html','history.html'].includes(page);
 useEffect(()=>{if(page==='login.html')window.history.replaceState(null,'','/login.html');api('auth/me').then(d=>{setUser(d.user);if(protectedPage&&!d.user)location.replace('/login.html');}).catch(e=>setNotice(e.message)).finally(()=>setReady(true));},[]);
 useEffect(()=>{if(page!=='index.html')return;let active=true;api('seasonal-looks?season='+encodeURIComponent(finder.season)).then(d=>{if(active)setLooks(d);}).catch(e=>{if(active)setNotice(e.message);});return()=>{active=false;};},[finder.season]);
 useEffect(()=>{if(!ready)return;if(page==='trends.html')api('trends').then(setTrends).catch(e=>setNotice(e.message));if(!user)return;
 if(page==='wardrobe.html')reloadCloset().catch(e=>setNotice(e.message));
 if(page==='profile.html')api('profile',{protect:true}).then(setProfile).catch(e=>setNotice(e.message));
 if(page==='history.html')api('outfits/history',{protect:true}).then(setHistory).catch(e=>setNotice(e.message));
 },[ready,user?.id]);
 useEffect(()=>{if(!finder.anchorCategory||!user){setColors([]);return;}let active=true;api('outfits/anchor-colors?category='+encodeURIComponent(finder.anchorCategory),{protect:true}).then(d=>{if(active)setColors(d);}).catch(e=>setNotice(e.message));return()=>{active=false;};},[finder.anchorCategory,user?.id]);
 async function reloadCloset(){const [a,b]=await Promise.all([api('items'),api('wardrobe',{protect:true})]);setItems(a);setCloset(b);setPick(v=>v||String(a[0]?.id||''));}
 async function action(fn){setBusy(true);setNotice('');try{await fn();}catch(e){setNotice(e.message);}finally{setBusy(false);}}
 async function logout(){await action(async()=>{await api('auth/logout',{method:'POST'});setUser(null);setCloset([]);setProfile(initialProfile);setPhotos({});setHistory([]);location.replace('/');});}
 async function choosePhoto(kind,file){const seq=(photoSequence.current[kind]||0)+1;photoSequence.current[kind]=seq;try{const photo=await readPhoto(file);if(photoSequence.current[kind]!==seq)return;setPhotos(v=>({...v,[kind]:photo}));if(kind==='garment'&&photo){try{const guess=await localColor(photo.file);if(photoSequence.current[kind]!==seq)return;if(guess){setGarment(v=>({...v,color_id:String(colorMap[guess])}));setAnalysis('기기 내 색상 추정: '+guess+'. 배경에 따라 틀릴 수 있으므로 확인·수정하세요.');}}catch(e){setAnalysis('기기 내 색상 추정이 어려워 직접 선택해 주세요.');}}}catch(e){setPhotos(v=>({...v,[kind]:null}));setAnalysis(e.message);}}
 async function analyzePhoto(kind){await action(async()=>{if(!photos[kind])throw Error('먼저 사진을 선택하세요.');if(!(kind==='garment'?consent.garment:consent.profile))throw Error('사진 AI 전송 동의가 필요합니다.');setAnalysis('분석 중…');const d=await api('vision/analyze',{method:'POST',body:{kind,consent:true,data:photos[kind].data},protect:true}),a=d.result;if(kind==='garment'){setGarment(v=>({...v,...(a.name?{name:a.name}:{}),...(categoryMap[a.category]?{category_id:String(categoryMap[a.category])}:{}),...(colorMap[a.color]?{color_id:String(colorMap[a.color])}:{}),...(['봄','여름','가을','겨울','사계절'].includes(a.season)?{season:a.season}:{})}));if(a.pattern&&a.pattern!=='알 수 없음')setPattern(a.pattern);}else{const field=kind==='face'?'face_shape':'body_shape';setProfile(v=>({...v,[field]:a[field]}));}setAnalysis('AI 분석 제안을 반영했습니다. 정확하지 않을 수 있으니 선택값을 확인·수정한 뒤 저장하세요.');});}
 function submitRecommend(e){e.preventDefault();if(!user){location.assign('/login.html');return;}action(async()=>{if(finder.anchorCategory&&!finder.anchorColor)throw Error('기준 색상을 선택하세요.');const body={...finder,budget:Number(finder.budget),anchorCategory:finder.anchorCategory||null,anchorColor:finder.anchorColor||null};const data=await api('outfits/recommend',{method:'POST',body,protect:true});setOutfits(data);setApplied(body);setSelected(null);});}
 function submitGarment(e){e.preventDefault();action(async()=>{const body={...garment};if(photos.garment){const d=await api('uploads',{method:'POST',body:{data:photos.garment.data},protect:true});body.image_url=d.image_url;}await api('wardrobe/custom',{method:'POST',body,protect:true});await reloadCloset();setGarment(initialGarment);setPhotos(v=>({...v,garment:null}));setAnalysis('');setPopup('내 옷을 등록했습니다.');});}
 function submitProfile(e){e.preventDefault();action(async()=>{await api('profile',{method:'PUT',body:profile,protect:true});setPopup('나의 스타일을 저장했습니다.');});}
 function submitAdmin(e){e.preventDefault();const body=Object.fromEntries(new FormData(e.currentTarget));action(async()=>{const d=await api('items',{method:'POST',body,protect:true});setPopup('상품 등록 완료 · ID '+d.id);});}
 function submitLogin(e){e.preventDefault();const body=Object.fromEntries(new FormData(e.currentTarget));action(async()=>{const d=await api('auth/request',{method:'POST',body});setNotice(d.message);});}
 function account(){return <Account user={user} logout={logout}/>}
 function transform(node,props){const id=props.id,name=props.name,owner=formOf(node);const out={};
 if(node.name==='header'&&String(props.className||'').includes('site-header'))out.children=<>{domToReact(node.children,{replace:replaceNode})}{account()}</>;
 if(node.name==='button')out.disabled=busy;
 if(node.name==='form')out.onSubmit=({recommendForm:submitRecommend,customForm:submitGarment,profileForm:submitProfile,f:submitAdmin,login:submitLogin})[id];
 if(Object.hasOwn(finder,id)&&['input','select'].includes(node.name)){out.value=finder[id];out.onChange=e=>{setFinder(v=>({...v,[id]:e.target.value,...(id==='anchorCategory'?{anchorColor:''}:{})}));if(id==='season')setSelected(null);};}
 if(id==='anchorColor'){out.disabled=!finder.anchorCategory;out.children=<><option value="">{finder.anchorCategory?'색상을 선택하세요':'먼저 기준 아이템을 선택하세요'}</option>{colors.map(c=><option key={c}>{c}</option>)}</>;}
 if(owner==='customForm'&&name&&Object.hasOwn(garment,name)){out.value=garment[name];out.onChange=e=>setGarment(v=>({...v,[name]:e.target.value}));}
 if(owner==='profileForm'&&name&&Object.hasOwn(profile,name)){out.value=profile[name];out.onChange=e=>setProfile(v=>({...v,[name]:e.target.value}));}
 if(id==='pattern'){out.value=pattern;out.onChange=e=>setPattern(e.target.value);}
 if(['garmentPhoto','facePhoto','bodyPhoto'].includes(id)){const kind=id.replace('Photo','');out.onChange=e=>choosePhoto(kind,e.target.files[0]);}
 if(id==='garmentPhoto')out['aria-describedby']='photoHint';
 if(id==='photoPreview'){out.src=photos.garment?.data;out.hidden=!photos.garment;}
 if(id==='facePreview'||id==='bodyPreview'){const kind=id.replace('Preview','');out.src=photos[kind]?.data;out.hidden=!photos[kind];}
 if(id==='garmentConsent'||id==='profileConsent'){const kind=id==='garmentConsent'?'garment':'profile';out.checked=consent[kind];out.onChange=e=>setConsent(v=>({...v,[kind]:e.target.checked}));}
 if(id==='analyzeGarment')out.onClick=()=>analyzePhoto('garment');if(id==='faceAnalyze')out.onClick=()=>analyzePhoto('face');if(id==='bodyAnalyze')out.onClick=()=>analyzePhoto('body');
 if(id==='photoHint')out.children=<>{photos.garment?'사진을 확인한 뒤 분석하거나 직접 선택해 등록하세요. 최대 3MB.':'휴대폰에서 사진을 선택하거나 바로 촬영할 수 있습니다. 최대 3MB.'}<label className="camera-picker">카메라로 옷 촬영<input type="file" accept="image/jpeg,image/png,image/webp" capture="environment" onChange={e=>choosePhoto('garment',e.target.files[0])}/></label></>;
 if(id==='garmentAnalysis'||id==='photoAnalysisStatus')out.children=analysis||'사진 선택 후 AI 전송에 동의하고 분석할 수 있습니다. 직접 선택도 가능합니다.';
 if(id==='bodyCardGrid')out.children=[['슬림형','slim'],['보통형','average'],['통통형','fuller']].map(([label,file])=><button key={file} type="button" className={'body-card'+(profile.body_shape===label?' selected':'')} aria-label={label} aria-pressed={profile.body_shape===label} onClick={()=>setProfile(v=>({...v,body_shape:label}))}><img src={'/images/body-'+file+'.svg'} alt={label+'을 나타내는 단순 실루엣 그림'}/><span>{label}</span></button>);
 if(id==='profileStatus')out.children=busy?'저장 중…':'선택값은 내 스타일 저장을 눌러야 적용됩니다.';
 if(id==='message'||id==='msg')out.children=notice;
 if(id==='pick'){out.value=pick;out.onChange=e=>setPick(e.target.value);out.children=items.map(i=><option value={i.id} key={i.id}>{i.category_name} · {i.name}</option>);}
 if(id==='add')out.onClick=()=>action(async()=>{await api('wardrobe',{method:'POST',body:{item_id:Number(pick)},protect:true});await reloadCloset();setPopup('내 옷장에 추가했습니다.');});
 if(id==='owned')out.children=closet.length?closet.map(i=><div className="closet-row" key={i.item_id}>{i.image_url&&<img src={i.image_url} alt={i.name} width="60" height="70" style={{objectFit:'cover',borderRadius:7}}/>}<span>{i.category_name} · {i.name} ({i.color_name})</span><span className="owned-text">보유 · 추가비용 0원</span><button className="secondary" onClick={()=>action(async()=>{await api('wardrobe/'+i.item_id,{method:'DELETE',protect:true});await reloadCloset();setNotice('옷장에서 제거했습니다.');})}>제거</button></div>):'아직 등록한 옷이 없습니다.';
 if(id==='seasonalLooks')out.children=looks.map(look=><article className="look-card" key={look.id}><img src={look.image_url} alt={look.title+' 참고용 코디 이미지'} loading="lazy"/><div className="look-details"><span className="eyebrow">{look.season} · LOOK {look.look_no}</span><h3>{look.title}</h3><p className="muted">{look.description}</p><span className="soft-label">{look.style_name} · 샘플 이미지</span></div></article>);
 if(id==='results')out.children=<>{busy&&<p>나만의 코디를 찾고 있습니다…</p>}{applied&&<div className="applied-notice">✓ 적용 조건: {applied.season} / {applied.style} / {applied.anchorCategory?applied.anchorColor+' '+applied.anchorCategory:'기준 옷 자동'} / {applied.source==='mixed'?'내 옷 우선':applied.source==='wardrobe'?'내 옷만':'쇼핑만'} / 예산 {won(applied.budget)}</div>}{outfits?.length===0&&<div className="empty">조건에 맞는 코디가 없습니다. 아우터·상의·하의·신발을 등록하거나 계절·스타일·색상·예산을 변경하세요.</div>}{outfits?.map((outfit,index)=><Outfit key={index} outfit={outfit} index={index} accepted={selected===index} anchor={applied?.anchorCategory?applied.anchorColor+' '+applied.anchorCategory:''} onChoose={()=>{setSelected(index);document.querySelector('#acceptedStatus')?.scrollIntoView({block:'nearest',behavior:'smooth'});}}/>)}</>;
 if(id==='acceptedStatus')out.children=selected===null?'아직 선택한 코디가 없습니다.':`✓ LOOK ${selected+1} 채택 완료 · 보유 의류 ${outfits[selected].owned_count}개 · 추가 구매 ${won(outfits[selected].purchase_total)} (화면 선택, DB 채택 저장 없음)`;
 if(id==='trends')out.children=trends.length?trends.map(t=><p key={t.id}>{t.year} {t.season} · {t.style_name} · 점수 {t.score} · {t.notes||''}</p>):'등록된 트렌드 없음';
 if(id==='history')out.children=history.length?history.map(row=><section className="panel" key={row.id}><h2>{new Date(row.created_at).toLocaleString()}</h2>{(typeof row.payload==='string'?JSON.parse(row.payload):row.payload).map((look,i)=><p key={i}>{look.items.map(item=>item.name).join(' · ')} / 추가 구매 {won(look.purchase_total)}</p>)}</section>):'아직 추천 이력이 없습니다.';
 if(id==='login')out.hidden=!!token;
 if(id==='verify'){out.hidden=!token;out.onClick=()=>action(async()=>{await api('auth/verify',{method:'POST',body:{token}});location.replace('/');});}
 if(id==='status')out.children=notice||(token?'아래 버튼을 눌러 이 기기에서 로그인을 완료하세요.':'');
 return out;
 }
 function replaceNode(node,index){if(node.type!=='tag')return;const props=attributesToProps(node.attribs||{}),change=transform(node,props);const {children,...extra}=change;return React.createElement(node.name,{...props,...extra,key:index},...(['input','img','br','hr','meta','link'].includes(node.name)?[]:[children!==undefined?children:domToReact(node.children||[],{replace:replaceNode})]));}
 return <>{!online&&<div role="status" className="app-notice">오프라인입니다. 개인 자료 조회·저장은 서버에 다시 연결한 후 사용할 수 있습니다.</div>}{notice&&page!=='login.html'&&<div role="status" className="app-notice">{notice}</div>}{protectedPage&&!ready?<main>로그인 상태를 확인하고 있습니다…</main>:(page==='mobile.html'?<Mobile/>:<Template name={page} transform={transform}/>)}<div className="device-footer">PC · 휴대폰 공용 / Fashion Balance AI</div>{popup&&<div className="modal-backdrop"><section className="panel success-dialog" role="dialog" aria-modal="true" aria-labelledby="saved-title"><h2 id="saved-title">저장 완료</h2><p>{popup}</p><div className="dialog-actions"><button autoFocus onClick={()=>location.assign('/')}>메인으로 돌아가기</button><button className="secondary" onClick={()=>setPopup('')}>계속 관리하기</button></div></section></div>}</>;
}
createRoot(document.getElementById('root')).render(<App/>);

if('serviceWorker' in navigator&&window.isSecureContext){window.addEventListener('load',()=>{navigator.serviceWorker.register('/sw.js').catch(()=>{});});}
