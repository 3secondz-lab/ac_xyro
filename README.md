
** ac_xyro -- Asseto Corsa in-game app to emulate Xyro **


**HISTORY:**
* 2020.04.14 - Alive packet 전송
             위치, 속도 NAV_PVT 패킷으로 전송

* 2020.04.07 - 게임 내 차량 데이터 읽어 UDP 전송

**설치 방법:**
1) sam_second_xyro 폴더를 폴더째 C:\Program Files (x86)\Steam\steamapps\common\assettocorsa\apps\python 로 복사
2) Assetto Corsa 설정에서 sam_second_xyro 앱 체크
3) 한번 실행하고 나면 내문서\Assetto Corsa\cfg\apps\3secondz_xyro.ini 생성되는데 안에 서버 ip/port 맞게 설정
4) 3Secondz 서버에 기기 등록 하고 실행 
(기기 번호는 sam_second_xyro.py 초반 DEVICE_ID에 설정. default ac00000000000001는 jongpil.jung@3secondz.com 계정에 이미 등록됨)

** 현재는 Assetto Corsa 용인 서킷에서만 동작함 **
서킷 다운로드: https://drive.google.com/file/d/1tS8-dOdjPKPYiDWrBq-6USR_7jqlrblb/view?usp=sharing


**TODO:**
- 프로토콜 맞춰 서버 연동


**PROTOCOL:**
1. 구현 완료
   - Alive
2 구현 중
   - NAV_PVT
3 구현 예정
   - Start
   - Stop
   - CAN Data
   - OBD Data
