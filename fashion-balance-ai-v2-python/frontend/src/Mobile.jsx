import React,{useEffect,useState} from 'react';

export default function Mobile(){
 const [config,setConfig]=useState(null),[error,setError]=useState(''),[prompt,setPrompt]=useState(null);
 useEffect(()=>{
  fetch('/api/mobile/config').then(async r=>{const d=await r.json();if(!r.ok)throw Error(d.error);setConfig(d);}).catch(e=>setError(e.message));
  const listener=e=>{e.preventDefault();setPrompt(e);};window.addEventListener('beforeinstallprompt',listener);
  return()=>window.removeEventListener('beforeinstallprompt',listener);
 },[]);
 return <main className="mobile-guide"><a href="/">← 메인으로 돌아가기</a><section className="panel"><span className="eyebrow">MOBILE GUIDE</span><h1>휴대폰에서 나의 코디 시작하기</h1><p>가입 QR을 스캔하면 같은 서버의 내 옷장으로 연결됩니다.</p>{error&&<p role="alert">{error}</p>}{config&&<><p className="mobile-url">{config.base_url}</p>{config.loopback&&<p className="app-notice">현재 주소는 PC 전용 localhost입니다. 설치 설명서에 따라 PC의 Wi-Fi IPv4 주소나 HTTPS 도메인으로 APP_BASE_URL을 설정하세요.</p>}<img className="signup-qr" src="/api/auth/qr" alt="가입 화면으로 이동하는 QR코드"/><a className="mobile-open" href="/login.html">이 기기에서 가입·로그인</a><p>{config.secure?'HTTPS 연결입니다. 지원 브라우저에서 앱 설치 또는 홈 화면 추가를 사용할 수 있습니다.':'일반 HTTP에서는 웹페이지 이용과 바로가기는 가능하지만 앱 설치·오프라인 껍데기 기능은 브라우저에 따라 제한됩니다.'}</p></>}<h2>홈 화면에 아이콘 추가</h2><ol><li>iPhone: Safari에서 열기 → 공유 → 홈 화면에 추가.</li><li>Android: Chrome 메뉴 → 앱 설치 또는 홈 화면에 추가.</li><li>아이콘을 누르면 같은 서버 주소로 열립니다. 실제 메뉴 이름은 브라우저 버전에 따라 다를 수 있습니다.</li></ol>{prompt&&<button onClick={async()=>{await prompt.prompt();setPrompt(null);}}>이 기기에 앱 설치</button>}<p className="muted">옷장·사진·체형·추천 이력은 서버와 MySQL에 보관합니다. PC 또는 운영 서버가 켜져 있어야 자료를 조회·저장할 수 있습니다. 오프라인에서는 개인 자료를 캐시하거나 수정하지 않습니다.</p><h2>사진 선택·촬영</h2><p>내 옷장에서는 저장된 사진 선택과 카메라 촬영을 모두 지원합니다. AI 분석은 사진 전송 동의 후 별도로 실행하며, 직접 선택해 저장할 수도 있습니다.</p></section></main>;
}
