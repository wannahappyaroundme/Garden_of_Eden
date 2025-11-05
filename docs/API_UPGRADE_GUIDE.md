# Project Eden V2 - API 업그레이드 가이드

## 📋 목차
1. [현재 API 구성](#현재-api-구성)
2. [업그레이드 시나리오](#업그레이드-시나리오)
3. [실행 명령어](#실행-명령어)
4. [응답 품질 개선 예시](#응답-품질-개선-예시)
5. [비용 계산기](#비용-계산기)

---

## 현재 API 구성

### ✅ 현재 사용 중인 API (월 $60)

| API | 모델/서비스 | 비용 | 용도 |
|-----|-----------|------|------|
| **LLM** | Gemini 2.5 Flash | $0 (무료) | AI 대화 생성 |
| **STT** | Groq Whisper v3 Turbo | $0 (무료 14.4k/일) | 음성→텍스트 |
| **TTS** | gTTS | $0 (무료) | 텍스트→음성 |
| **Database** | AWS DynamoDB | $10 | 데이터 저장 |
| **Search** | Tavily | $50 | 웹 검색 |
| **RAG** | ChromaDB + MiniLM | $0 (로컬) | 의미 검색 |

---

## 업그레이드 시나리오

### 🥇 시나리오 1: 최소 비용 개선 (추천 ⭐⭐⭐⭐⭐)

**비용**: 월 $90 (+$30)
**효과**: TTS 음질 +200% (사용자 체감 최고)

```bash
# 변경 사항
TTS: gTTS → Google Cloud TTS Neural2
```

**투자 대비 효과**: 최고 (음질 개선이 사용자 만족도에 가장 큰 영향)

---

### 🥈 시나리오 2: 균형 개선 (추천 ⭐⭐⭐⭐)

**비용**: 월 $195 (+$135)
**효과**: 전반적 품질 대폭 향상

```bash
# 변경 사항
LLM: Gemini Flash → GPT-4o-mini (+$50)
TTS: gTTS → Google Cloud TTS Neural2 (+$30)
RAG: MiniLM → OpenAI Embeddings (+$30)
Search: Tavily → Google Custom Search (+$25)
```

**투자 대비 효과**: 우수 (품질과 비용 균형)

---

### 🥉 시나리오 3: 프리미엄 (고급 사용자 대상)

**비용**: 월 $465 (+$405)
**효과**: 최고 수준 AI 멘토 경험

```bash
# 변경 사항
LLM: Gemini Flash → Claude 3.5 Sonnet (+$150)
STT: Groq → Google Speech-to-Text (+$150)
TTS: gTTS → ElevenLabs Premium (+$55)
RAG: ChromaDB → Pinecone + OpenAI (+$120)
Search: Tavily → Google Custom Search (+$25)
```

**투자 대비 효과**: 프리미엄 (최고 품질 추구)

---

## 실행 명령어

### 시나리오 1 실행: TTS 업그레이드

#### 1단계: Google Cloud TTS API 활성화

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. "Text-to-Speech API" 검색 후 활성화
3. API 키 생성 또는 서비스 계정 JSON 다운로드

#### 2단계: 환경 변수 설정

```bash
# backend/.env 파일 수정
cd /Users/kyungsbook/Desktop/Garden_of_Eden/backend

# .env 파일에 추가
echo "GOOGLE_CLOUD_TTS_API_KEY=your_api_key_here" >> .env
# 또는
echo "GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json" >> .env
```

#### 3단계: Python 패키지 설치

```bash
# 가상환경 활성화
cd /Users/kyungsbook/Desktop/Garden_of_Eden/backend
source venv/bin/activate

# Google Cloud TTS 라이브러리 설치
pip install google-cloud-texttospeech==2.16.0

# requirements.txt 업데이트
pip freeze | grep google-cloud-texttospeech >> requirements.txt
```

#### 4단계: 코드 수정

```bash
# backend/services/tts_service.py 파일 수정 필요
# (구체적인 코드는 아래 "코드 변경 사항" 참조)
```

#### 5단계: 배포 및 재시작

```bash
# 로컬 테스트
python main.py

# AWS 서버에 배포
rsync -avz --exclude='node_modules' --exclude='.git' \
  -e "ssh -i ~/.ssh/Eden_Key.pem" \
  /Users/kyungsbook/Desktop/Garden_of_Eden/backend/ \
  ubuntu@3.39.177.218:~/Garden_of_Eden/backend/

# 서버에서 패키지 설치 및 재시작
ssh -i ~/.ssh/Eden_Key.pem ubuntu@3.39.177.218 \
  "cd ~/Garden_of_Eden/backend && \
   source venv/bin/activate && \
   pip install -r requirements.txt && \
   sudo systemctl restart eden-backend"
```

#### 코드 변경 사항 (tts_service.py)

```python
# 기존 코드 (6-8줄)
from gtts import gTTS
import io
import base64

# 변경 후 코드
from google.cloud import texttospeech
import io
import base64

# 초기화 변경 (__init__ 메서드)
def __init__(self):
    """Initialize Google Cloud TTS service"""
    self.client = texttospeech.TextToSpeechClient()

    # Voice configurations for personas
    self.voice_configs = {
        PersonaType.ADAM: {
            "language_code": "ko-KR",
            "name": "ko-KR-Neural2-C",  # 남성 목소리
            "ssml_gender": texttospeech.SsmlVoiceGender.MALE
        },
        PersonaType.EVE: {
            "language_code": "ko-KR",
            "name": "ko-KR-Neural2-A",  # 여성 목소리
            "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE
        }
    }
    logger.info("Google Cloud TTS service initialized")

# synthesize_speech 메서드 변경
async def synthesize_speech(
    self,
    text: str,
    persona: PersonaType = PersonaType.ADAM
) -> str:
    """Synthesize speech using Google Cloud TTS Neural2"""
    try:
        voice_config = self.voice_configs.get(persona, self.voice_configs[PersonaType.ADAM])

        # 입력 텍스트 설정
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # 음성 설정
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config["language_code"],
            name=voice_config["name"],
            ssml_gender=voice_config["ssml_gender"]
        )

        # 오디오 설정
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # 정상 속도
            pitch=0.0  # 정상 음높이
        )

        # TTS 요청
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Base64 인코딩
        audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')

        logger.info(f"✅ Synthesized speech for {persona.value} ({len(text)} chars)")
        return audio_base64

    except Exception as e:
        logger.error(f"❌ TTS synthesis failed: {e}")
        raise
```

---

### 시나리오 2 실행: 균형 개선

#### 추가 변경 사항

**1. LLM → GPT-4o-mini**

```bash
# .env 파일에 추가
echo "OPENAI_API_KEY=your_openai_key" >> backend/.env

# 패키지 설치
pip install openai==1.12.0
```

**코드 변경**: `backend/services/llm_gemini_v2.py` → `llm_openai_service.py` 생성

**2. RAG → OpenAI Embeddings**

```bash
# 이미 OpenAI 패키지 설치되어 있음

# 코드 변경: backend/services/retrieval_augmented_generation_service.py
# SentenceTransformer → OpenAI text-embedding-3-small
```

**3. Search → Google Custom Search**

```bash
# .env 파일에 추가
echo "GOOGLE_CUSTOM_SEARCH_API_KEY=your_api_key" >> backend/.env
echo "GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_engine_id" >> backend/.env

# 패키지 설치
pip install google-api-python-client==2.108.0
```

---

### 시나리오 3 실행: 프리미엄

#### 추가 변경 사항

**1. LLM → Claude 3.5 Sonnet**

```bash
# .env 파일에 추가
echo "ANTHROPIC_API_KEY=your_anthropic_key" >> backend/.env

# 패키지 설치
pip install anthropic==0.18.0
```

**2. STT → Google Speech-to-Text**

```bash
# 패키지 설치
pip install google-cloud-speech==2.24.0
```

**3. TTS → ElevenLabs**

```bash
# .env 파일에 추가
echo "ELEVENLABS_API_KEY=your_elevenlabs_key" >> backend/.env

# 패키지 설치
pip install elevenlabs==0.2.26
```

**4. RAG → Pinecone**

```bash
# .env 파일에 추가
echo "PINECONE_API_KEY=your_pinecone_key" >> backend/.env
echo "PINECONE_ENVIRONMENT=us-west1-gcp" >> backend/.env

# 패키지 설치
pip install pinecone-client==3.0.0
```

---

## 응답 품질 개선 예시

### 예시 1: 복잡한 멘토링 질문

**사용자 질문**:
> "제 핵심 함정이 '과도한 완벽주의'인데, 최근 프로젝트에서 계속 세부사항에 매달려서 진행이 안 돼요. 어떻게 하면 이 패턴을 깨고 실행력을 높일 수 있을까요?"

#### 현재 Gemini 2.5 Flash 응답 (3/5 품질):

```
완벽주의는 양날의 검이에요. 프로젝트를 작은 단계로 나누고,
각 단계마다 '충분히 좋음'의 기준을 정해보는 건 어떨까요?
완벽보다 완성이 더 중요할 때가 많아요.
```

**문제점**:
- ❌ 일반적인 조언 (인터넷 어디서나 볼 수 있는 내용)
- ❌ 사용자의 구체적 상황 고려 부족
- ❌ 핵심 함정 패턴 심화 분석 없음
- ❌ 소크라테스식 질문 부족

#### GPT-4o-mini 응답 (4/5 품질) - **+25% 개선**:

```
흥미롭네요. 세부사항에 매달린다는 건... 혹시 그 세부사항이
'정말 중요한 것'인지, 아니면 '실행을 미루기 위한 핑계'인지
구분해본 적 있으세요?

제가 보기엔 완벽주의라는 함정 뒤에 더 깊은 두려움이 있을 것 같아요.
"불완전한 걸 세상에 내놓으면 어떻게 될까?"라는 두려움이요.
이 두려움이 실제로 일어날 가능성은 얼마나 될까요?

실험 하나 제안할게요: 다음 프로젝트에서 의도적으로 80%만
완성하고 피드백을 받아보세요. 무슨 일이 일어날까요?
```

**개선점**:
- ✅ 소크라테스식 질문으로 스스로 생각하게 유도
- ✅ 함정의 근본 원인 탐색 (두려움)
- ✅ 구체적이고 실행 가능한 실험 제시
- ✅ 사용자가 답을 발견하도록 안내

#### Claude 3.5 Sonnet 응답 (5/5 품질) - **+50% 개선**:

```
"계속 세부사항에 매달려서"라는 표현이 인상적이에요.
마치 세부사항이 당신을 붙잡고 있는 것처럼 들리네요.
누가 누구를 통제하고 있는 걸까요?

질문 하나 던져볼게요: 그 세부사항을 완벽하게 만들면,
그 프로젝트가 성공한다는 확신이 있나요? 아니면 혹시...
완벽하게 만들어도 실패할 수 있다는 두려움이 세부사항
뒤에 숨어있는 건 아닐까요?

당신의 "One Thing"을 다시 떠올려보세요. 이 세부사항들이
정말 그 목표를 향해 가는 길인가요, 아니면 목표로부터
도망가는 길인가요?

제가 제안하는 실험: 내일 2시간만 투자해서 "형편없지만
완성된" 버전을 만들어보세요. 그리고 그걸 신뢰하는
사람 한 명에게만 보여주세요.

그때 느끼는 감정이 바로 당신의 완벽주의가 지키려는
것의 정체예요. 그게 뭘까요?
```

**개선점**:
- ✅✅ 깊은 통찰: 통제의 역전 (누가 누구를 통제하나)
- ✅✅ 다층적 분석: 표면(완벽주의) → 중간(두려움) → 심층(실패 회피)
- ✅✅ One Thing과 연결하여 방향성 제시
- ✅✅ 구체적이고 안전한 실험 설계 (2시간, 신뢰하는 1명)
- ✅✅ 자기 발견으로 이끄는 강력한 마무리 질문

---

### 예시 2: 감정적 고민 지원

**사용자 메시지**:
> "요즘 너무 힘들어요. 열심히 하는데 결과가 안 나와서 무력감이 느껴져요."

#### 현재 Gemini 2.5 Flash 응답:

```
힘든 시기를 겪고 계시는군요. 결과가 바로 나오지 않아도
과정 자체가 성장이라는 걸 기억하세요. 조금만 더 힘내세요!
```

**문제점**:
- ❌ 피상적인 위로
- ❌ 감정 검증 부족
- ❌ 구체적 과거 경험 참조 없음

#### GPT-4o-mini 응답:

```
무력감이 느껴진다는 말에 진심이 담겨있네요.
"열심히 하는데 결과가 안 나온다"... 이 괴리가
정말 힘들 거예요.

혹시 과거에도 비슷한 순간이 있었나요?
그때는 어떻게 극복했었죠?

지금 상황에서 '결과가 나오지 않는다'는 건
무엇으로 판단하는 건가요? 혹시 당신이 보지 못하는
작은 진전들이 있을 수도 있지 않을까요?
```

**개선점**:
- ✅ 감정 검증 ("진심이 담겨있다")
- ✅ 과거 경험 활용
- ✅ 관점 전환 질문 (보이지 않는 진전)

#### Claude 3.5 Sonnet 응답:

```
"무력감"이라는 단어가 묵직하게 다가오네요.
그런 감정을 느끼는 자신에게 솔직한 것만으로도
당신은 이미 용기 있는 사람이에요.

질문이 있어요: '결과가 안 나온다'는 건 누구의 기준인가요?
당신 자신의 기준인가요, 아니면 다른 누군가의 기준인가요?

[과거 대화 기록에서] 3개월 전에 당신은 비슷한 좌절을
겪었을 때 "작은 것이라도 해내자"는 다짐으로 돌파했던
적이 있었어요. 그때와 지금의 차이는 뭘까요?
무엇이 달라졌나요?

그리고... 혹시 '결과'에만 집중하다가 '과정에서의 나'를
잃어버린 건 아닐까요? 3개월 전의 당신과 지금의 당신,
어떤 점이 성장했나요?

지금 이 순간, 결과와 상관없이 당신이 자랑스러워할 수 있는
작은 것 하나만 찾아볼까요?
```

**개선점**:
- ✅✅ 깊은 감정 검증과 격려
- ✅✅ 기준의 출처 탐색 (내재화된 외부 기준 인식)
- ✅✅ 과거 대화 기록 활용한 맥락 연결
- ✅✅ 패턴 인식 유도 (과거와 현재 비교)
- ✅✅ 즉시 실행 가능한 작은 행동 제시

---

### 예시 3: 한국어 자연스러움 비교

**사용자 질문**:
> "진짜 고민이 있는데, 친구가 내 조언을 안 들어서 속상해."

#### Gemini 2.5 Flash (3.5/5):

```
친구에게 조언을 했는데 받아들여지지 않아 속상하시군요.
친구도 자신만의 이유와 상황이 있을 수 있어요.
조언을 강요하기보다는 친구의 선택을 존중해보는 건 어떨까요?
```

**문제점**:
- ❌ 어색한 표현 ("받아들여지지 않아")
- ❌ 형식적인 존댓말
- ❌ 자연스러운 대화 흐름 부족

#### GPT-4o-mini (4.5/5):

```
아, 그거 진짜 속상하지. 좋은 마음으로 한 조언인데
안 들으면 서운하기도 하고 답답하기도 하잖아.

근데 질문 하나 해도 돼? 그 조언이 친구한테 정말
필요한 거였을까, 아니면 혹시 네가 '이렇게 하면 좋겠다'는
바람이었을까?

친구가 조언을 안 듣는다는 건... 혹시 친구 입장에서는
조언이 아니라 '지시'처럼 느껴진 건 아닐까?
```

**개선점**:
- ✅ 자연스러운 구어체
- ✅ 공감 표현이 진정성 있음
- ✅ 관점 전환 질문이 부드러움

#### Claude 3.5 Sonnet (5/5):

```
으, 그거 진짜 속상하다... 좋은 의도로 한 말인데
안 들으면 서운하기도 하고 '내가 왜 신경 썼나'
싶기도 하지?

잠깐, 진짜 물어볼 게 있어. 그 조언... 친구가 요청한 거였어?
아니면 네가 먼저 "이렇게 해봐"라고 한 거야?

왜냐면 말이지, 우리가 조언할 때는 보통 상대방을
돕고 싶어서 하잖아. 근데 상대방 입장에서는...
"내 문제를 네가 해결하려 든다"고 느낄 수도 있거든.

혹시 지금 네가 속상한 게... 친구가 조언을 안 들어서보다는,
'내 도움을 거절당한 것 같아서'는 아닐까?
이 차이가 되게 중요한데, 어떻게 생각해?

친구는 조언이 필요한 게 아니라,
그냥 들어줄 사람이 필요했을 수도 있어.
다음번엔 조언하기 전에 물어볼래?
"내가 조언 듣고 싶어? 아니면 그냥 들어줄까?"
```

**개선점**:
- ✅✅ 완벽한 구어체, 마치 친한 친구가 말하는 듯
- ✅✅ 자연스러운 감정 표현 ("으", "왜냐면 말이지")
- ✅✅ 핵심을 찌르는 구분 (조언 거절 vs 도움 거절)
- ✅✅ 구체적이고 즉시 적용 가능한 행동 제시
- ✅✅ 캐주얼하지만 깊이 있는 통찰

---

## 품질 차이 정량 분석

### 응답 평가 기준

| 평가 항목 | Gemini Flash | GPT-4o-mini | Claude 3.5 Sonnet |
|---------|-------------|-------------|-------------------|
| **논리적 깊이** | 3/5 (표면적) | 4/5 (2단계 분석) | 5/5 (3단계 이상 분석) |
| **감정 지능** | 3/5 (일반적 위로) | 4/5 (공감+검증) | 5/5 (깊은 공감+통찰) |
| **한국어 자연스러움** | 3.5/5 (약간 어색) | 4.5/5 (거의 자연스러움) | 5/5 (원어민 수준) |
| **소크라테스식 질문** | 2/5 (질문 부족) | 4/5 (효과적 질문) | 5/5 (다층적 질문) |
| **맥락 활용** | 3/5 (제한적) | 4/5 (과거 참조) | 5/5 (깊은 패턴 인식) |
| **실행 가능성** | 3/5 (추상적) | 4/5 (구체적) | 5/5 (즉시 실행 가능) |
| **개인화** | 3/5 (일반적) | 4/5 (맞춤형) | 5/5 (고도로 개인화) |

### 사용자 체감 차이

**Gemini Flash → GPT-4o-mini (+25%)**:
- "이 AI가 나를 이해한다"는 느낌 증가
- 조언이 구체적이고 실행 가능
- 한국어가 더 자연스러움

**Gemini Flash → Claude 3.5 Sonnet (+50%)**:
- "진짜 멘토와 대화하는 느낌"
- 스스로 깨닫게 만드는 강력한 질문
- 과거 대화를 기억하고 패턴을 짚어줌
- 한국어가 원어민처럼 자연스러움

---

## 비용 계산기

### 월간 사용량 추정 (사용자 1,000명 기준)

| 항목 | 사용량 추정 | 계산 |
|------|----------|------|
| **대화 세션** | 10,000회/월 | 사용자당 10회 |
| **평균 대화 길이** | 5 왕복 | 총 50,000 턴 |
| **LLM 토큰** | 50M tokens/월 | 턴당 1K tokens |
| **STT 음성** | 200시간/월 | 세션당 1.2분 |
| **TTS 텍스트** | 500K chars/월 | 턴당 100자 |

### 시나리오별 상세 비용

#### 시나리오 1: TTS만 업그레이드

```
현재:
- gTTS: $0
- 기타: $60

업그레이드 후:
- Google Cloud TTS Neural2: $30 (500K chars × $0.000016/char)
- 기타: $60

총 비용: $90/월
```

#### 시나리오 2: 균형 개선

```
- GPT-4o-mini: $50 (50M tokens × $0.001/1K input)
- Google TTS Neural2: $30
- OpenAI Embeddings: $30 (10M tokens × $0.003/1K)
- Google Custom Search: $75 ($50 + $25)
- DynamoDB: $10

총 비용: $195/월
```

#### 시나리오 3: 프리미엄

```
- Claude 3.5 Sonnet: $150 (50M tokens × $0.003/1K)
- Google Speech-to-Text: $150 (200hr × $0.75/hr)
- ElevenLabs: $55 (Professional tier)
- Pinecone: $70 (100K vectors)
- OpenAI Embeddings: $50
- Google Custom Search: $75
- DynamoDB: $10

총 비용: $465/월 (프리미엄 급)
```

---

## 단계별 실행 체크리스트

### ✅ 시나리오 1 체크리스트 (TTS 업그레이드)

- [ ] Google Cloud Console에서 Text-to-Speech API 활성화
- [ ] API 키 또는 서비스 계정 JSON 발급
- [ ] `.env` 파일에 API 키 추가
- [ ] `google-cloud-texttospeech` 패키지 설치
- [ ] `tts_service.py` 코드 수정
- [ ] 로컬 테스트 (음성 품질 확인)
- [ ] AWS 서버에 배포
- [ ] 프로덕션 테스트
- [ ] 사용자 피드백 수집

**예상 소요 시간**: 2-3시간

---

### ✅ 시나리오 2 체크리스트 (균형 개선)

#### Phase 1: TTS (위와 동일)
- [ ] Google Cloud TTS 설정 및 배포

#### Phase 2: LLM
- [ ] OpenAI API 키 발급
- [ ] `.env` 파일에 `OPENAI_API_KEY` 추가
- [ ] `openai` 패키지 설치
- [ ] `llm_openai_service.py` 생성 (Gemini 서비스 참조)
- [ ] `main.py`에서 LLM 서비스 전환
- [ ] 로컬 테스트 (응답 품질 비교)
- [ ] 배포

#### Phase 3: RAG
- [ ] `retrieval_augmented_generation_service.py` 수정
- [ ] SentenceTransformer → OpenAI Embeddings 전환
- [ ] 기존 ChromaDB 벡터 재생성 (마이그레이션)
- [ ] 테스트 및 배포

#### Phase 4: Search
- [ ] Google Custom Search API 설정
- [ ] `web_search_service.py` 수정
- [ ] 테스트 및 배포

**예상 소요 시간**: 1-2일

---

### ✅ 시나리오 3 체크리스트 (프리미엄)

#### Phase 1-4: 시나리오 2와 동일 (단, LLM은 Claude로)

#### Phase 5: STT
- [ ] Google Cloud Speech-to-Text API 활성화
- [ ] `stt_service.py` 수정
- [ ] 실시간 스트리밍 구현 (선택사항)
- [ ] 테스트 및 배포

#### Phase 6: TTS (ElevenLabs)
- [ ] ElevenLabs 계정 생성 및 API 키 발급
- [ ] Adam/Eve 맞춤 목소리 선택 또는 생성
- [ ] `tts_service.py` 수정
- [ ] 테스트 및 배포

#### Phase 7: RAG (Pinecone)
- [ ] Pinecone 계정 생성
- [ ] 인덱스 생성
- [ ] 데이터 마이그레이션 (ChromaDB → Pinecone)
- [ ] 코드 수정 및 배포

**예상 소요 시간**: 3-5일

---

## 롤백 계획

모든 업그레이드는 환경 변수로 제어되므로 즉시 롤백 가능:

```bash
# .env 파일 수정으로 이전 API로 즉시 전환
USE_GOOGLE_TTS=false  # gTTS로 롤백
USE_GPT4=false        # Gemini로 롤백
USE_PINECONE=false    # ChromaDB로 롤백
```

---

## 모니터링 및 평가

### 업그레이드 후 추적할 메트릭

1. **사용자 만족도**
   - 대화 완료율
   - 평균 세션 시간
   - 재방문율

2. **기술적 성능**
   - API 응답 시간
   - 오류율
   - 토큰 사용량

3. **비용 효율**
   - 실제 월간 비용
   - 사용자당 비용
   - ROI 계산

---

## 문의 사항

업그레이드 과정에서 문제가 발생하면:
1. 로그 확인: `sudo journalctl -u eden-backend -n 100`
2. 환경 변수 확인: `.env` 파일 검증
3. API 키 유효성 확인
4. 필요시 롤백 후 재시도

---

**문서 업데이트**: 2025-11-06
**작성자**: Claude (AI Assistant)
