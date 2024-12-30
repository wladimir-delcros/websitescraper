"""
Mots-clés multilingues pour la détection des numéros de téléphone
"""

PHONE_KEYWORDS = [
    # Français
    r'tel|tél|telephone|téléphone|mobile|portable|fax|standard|numéro|numero|contact|appel|urgence|service|hotline|assistance|bureau|direct|fixe|accueil',
    
    # English
    r'phone|cell|mobile|contact|call|fax|dial|number|hotline|support|office|desk|extension|ext|emergency|service|direct|line|reach|reception|switchboard',
    
    # Deutsch (Allemand)
    r'telefon|handy|mobil|fax|rufnummer|durchwahl|notfall|büro|zentrale|anruf|kontakt|service|festnetz',
    
    # Español (Espagnol)
    r'teléfono|tel|móvil|celular|fijo|fax|llamada|contacto|urgencia|oficina|directo|servicio|central|recepción',
    
    # Italiano (Italien)
    r'telefono|cellulare|mobile|fisso|fax|chiamata|contatto|urgenza|ufficio|diretto|servizio|centralino',
    
    # Português (Portugais)
    r'telefone|celular|móvel|fixo|fax|chamada|contato|urgência|escritório|direto|serviço|central',
    
    # Nederlands (Néerlandais)
    r'telefoon|mobiel|vast|fax|nummer|contact|noodgeval|kantoor|direct|service|centraal',
    
    # Polski (Polonais)
    r'telefon|komórka|komorkowy|faks|numer|kontakt|nagły|biuro|bezpośredni|serwis|centrala',
    
    # Русский (Russe)
    r'телефон|мобильный|сотовый|факс|номер|контакт|экстренный|офис|прямой|сервис|центральный',
    
    # 中文 (Chinois)
    r'电话|手机|传真|号码|联系|紧急|办公室|直线|服务|总机',
    
    # 日本語 (Japonais)
    r'電話|携帯|ファックス|番号|連絡|緊急|事務所|直通|サービス|代表',
    
    # 한국어 (Coréen)
    r'전화|휴대폰|팩스|번호|연락처|긴급|사무실|직통|서비스|대표',
    
    # العربية (Arabe)
    r'هاتف|جوال|فاكس|رقم|اتصال|طوارئ|مكتب|مباشر|خدمة|مركز',
    
    # Türkçe (Turc)
    r'telefon|cep|faks|numara|iletişim|acil|ofis|direkt|servis|santral',
    
    # Svenska (Suédois)
    r'telefon|mobil|fax|nummer|kontakt|nödfall|kontor|direkt|service|växel',
    
    # Dansk (Danois)
    r'telefon|mobil|fax|nummer|kontakt|nødsituation|kontor|direkte|service|central',
    
    # Suomi (Finnois)
    r'puhelin|mobiili|faksi|numero|yhteystieto|hätä|toimisto|suora|palvelu|keskus',
    
    # Tiếng Việt (Vietnamien)
    r'điện thoại|di động|fax|số|liên hệ|khẩn cấp|văn phòng|trực tiếp|dịch vụ|tổng đài',
    
    # हिंदी (Hindi)
    r'फोन|मोबाइल|फैक्स|नंबर|संपर्क|आपातकालीन|कार्यालय|सीधा|सेवा|केंद्रीय',
    
    # Bahasa Indonesia (Indonésien)
    r'telepon|ponsel|faks|nomor|kontak|darurat|kantor|langsung|layanan|sentral',
    
    # Mots génériques et abréviations internationales
    r'gsm|voip|pbx|pabx|ip-phone|dect|callback|callcenter|helpline|helpdesk|info|support|contact',
    
    # Applications de messagerie/appel
    r'whatsapp|viber|telegram|signal|wechat|line|skype|zoom|teams|messenger',
    
    # Symboles et caractères spéciaux
    r'☎|📞|📱|📲|✆|℡'
]

# Patterns à exclure (identifiants, timestamps, etc.)
EXCLUDE_PATTERNS = [
    r'^\d{10}$',  # Juste 10 chiffres sans contexte
    r'\d{13}',    # Timestamps en millisecondes
    r'\d{10}\.?\d*',  # Timestamps avec décimales
    r'(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])',  # Dates
    r'area[-_]?\d+',  # Identifiants d'aire
    r'v\d+',      # Versions
    r'id[-_]?\d+',  # IDs
    r'[a-zA-Z][-_]?\d+',  # Codes alphanumériques
    r'\d+\.?\d*[x×]\d+\.?\d*',  # Dimensions
    r'\d+\.?\d*(?:px|em|rem|%|pt|ms)',  # Mesures CSS
    r'\d+\.?\d*(?:kb|mb|gb|tb)',  # Tailles de fichiers
    r'#\d+',      # Numéros de référence
    r'rgb\(\d+,\s*\d+,\s*\d+\)',  # Couleurs RGB
    r'rgba\(\d+,\s*\d+,\s*\d+,\s*[\d.]+\)',  # Couleurs RGBA
    r'\d+\s*x\s*\d+\s*(?:px|pixels)?',  # Dimensions d'images
    r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',  # UUIDs
    r'(?:v|version|ver)[-_. ]?\d+(?:\.\d+)*',  # Versions de logiciels
    r'r\d+',      # Révisions
    r'(?:page|p)[-_]?\d+',  # Numéros de page
    r'(?:size|width|height|top|left|right|bottom|padding|margin)[-_]?\d+',  # Propriétés CSS
    r'(?:row|col)[-_]?\d+',  # Indices de grille
    r'index[-_]?\d+',  # Indices
    r'item[-_]?\d+',  # Items
    r'section[-_]?\d+',  # Sections
    r'timestamp[-_]?\d+',  # Timestamps explicites
    r'added(?:on|at)[-_]?\d+',  # Dates d'ajout
    r'modified(?:on|at)[-_]?\d+',  # Dates de modification
    r'created(?:on|at)[-_]?\d+',  # Dates de création
    r'updated(?:on|at)[-_]?\d+',  # Dates de mise à jour
]
