"""
Codes téléphoniques internationaux et leurs préfixes locaux
Format: 'CODE_PAYS': ('CODE_TELEPHONIQUE', 'PREFIXE_LOCAL')
Si PREFIXE_LOCAL est None, aucun préfixe n'est ajouté
"""

COUNTRY_CODES = {
    'AF': ('93', '0'),     # Afghanistan
    'AL': ('355', '0'),    # Albanie
    'DZ': ('213', '0'),    # Algérie
    'AD': ('376', None),   # Andorre
    'AO': ('244', None),   # Angola
    'AR': ('54', '0'),     # Argentine
    'AM': ('374', '0'),    # Arménie
    'AU': ('61', '0'),     # Australie
    'AT': ('43', '0'),     # Autriche
    'AZ': ('994', '0'),    # Azerbaïdjan
    'BH': ('973', None),   # Bahreïn
    'BD': ('880', '0'),    # Bangladesh
    'BY': ('375', '0'),    # Biélorussie
    'BE': ('32', '0'),     # Belgique
    'BJ': ('229', None),   # Bénin
    'BT': ('975', None),   # Bhoutan
    'BO': ('591', '0'),    # Bolivie
    'BA': ('387', '0'),    # Bosnie-Herzégovine
    'BW': ('267', None),   # Botswana
    'BR': ('55', '0'),     # Brésil
    'BN': ('673', None),   # Brunei
    'BG': ('359', '0'),    # Bulgarie
    'BF': ('226', None),   # Burkina Faso
    'BI': ('257', None),   # Burundi
    'KH': ('855', '0'),    # Cambodge
    'CM': ('237', None),   # Cameroun
    'CA': ('1', '1'),      # Canada
    'CV': ('238', None),   # Cap-Vert
    'CF': ('236', None),   # République centrafricaine
    'TD': ('235', None),   # Tchad
    'CL': ('56', '0'),     # Chili
    'CN': ('86', '0'),     # Chine
    'CO': ('57', '0'),     # Colombie
    'KM': ('269', None),   # Comores
    'CG': ('242', None),   # Congo
    'CD': ('243', '0'),    # République démocratique du Congo
    'CR': ('506', None),   # Costa Rica
    'HR': ('385', '0'),    # Croatie
    'CU': ('53', '0'),     # Cuba
    'CY': ('357', None),   # Chypre
    'CZ': ('420', None),   # République tchèque
    'DK': ('45', None),    # Danemark
    'DJ': ('253', None),   # Djibouti
    'DO': ('1', '1'),      # République dominicaine
    'EC': ('593', '0'),    # Équateur
    'EG': ('20', '0'),     # Égypte
    'SV': ('503', None),   # Salvador
    'GQ': ('240', None),   # Guinée équatoriale
    'ER': ('291', '0'),    # Érythrée
    'EE': ('372', None),   # Estonie
    'ET': ('251', '0'),    # Éthiopie
    'FJ': ('679', None),   # Fidji
    'FI': ('358', '0'),    # Finlande
    'FR': ('33', '0'),     # France
    'GA': ('241', None),   # Gabon
    'GM': ('220', None),   # Gambie
    'GE': ('995', '0'),    # Géorgie
    'DE': ('49', '0'),     # Allemagne
    'GH': ('233', '0'),    # Ghana
    'GR': ('30', None),    # Grèce
    'GL': ('299', None),   # Groenland
    'GT': ('502', None),   # Guatemala
    'GN': ('224', None),   # Guinée
    'GW': ('245', None),   # Guinée-Bissau
    'GY': ('592', None),   # Guyana
    'HT': ('509', None),   # Haïti
    'HN': ('504', None),   # Honduras
    'HK': ('852', None),   # Hong Kong
    'HU': ('36', '06'),    # Hongrie
    'IS': ('354', None),   # Islande
    'IN': ('91', '0'),     # Inde
    'ID': ('62', '0'),     # Indonésie
    'IR': ('98', '0'),     # Iran
    'IQ': ('964', '0'),    # Irak
    'IE': ('353', '0'),    # Irlande
    'IL': ('972', '0'),    # Israël
    'IT': ('39', None),    # Italie
    'CI': ('225', None),   # Côte d'Ivoire
    'JM': ('1', '1'),      # Jamaïque
    'JP': ('81', '0'),     # Japon
    'JO': ('962', '0'),    # Jordanie
    'KZ': ('7', '8'),      # Kazakhstan
    'KE': ('254', '0'),    # Kenya
    'KI': ('686', None),   # Kiribati
    'KP': ('850', '0'),    # Corée du Nord
    'KR': ('82', '0'),     # Corée du Sud
    'KW': ('965', None),   # Koweït
    'KG': ('996', '0'),    # Kirghizistan
    'LA': ('856', '0'),    # Laos
    'LV': ('371', None),   # Lettonie
    'LB': ('961', '0'),    # Liban
    'LS': ('266', None),   # Lesotho
    'LR': ('231', None),   # Libéria
    'LY': ('218', '0'),    # Libye
    'LI': ('423', None),   # Liechtenstein
    'LT': ('370', '8'),    # Lituanie
    'LU': ('352', None),   # Luxembourg
    'MO': ('853', None),   # Macao
    'MK': ('389', '0'),    # Macédoine du Nord
    'MG': ('261', '0'),    # Madagascar
    'MW': ('265', None),   # Malawi
    'MY': ('60', '0'),     # Malaisie
    'MV': ('960', None),   # Maldives
    'ML': ('223', None),   # Mali
    'MT': ('356', None),   # Malte
    'MH': ('692', '1'),    # Îles Marshall
    'MR': ('222', None),   # Mauritanie
    'MU': ('230', None),   # Maurice
    'MX': ('52', '01'),    # Mexique
    'FM': ('691', '1'),    # Micronésie
    'MD': ('373', '0'),    # Moldavie
    'MC': ('377', None),   # Monaco
    'MN': ('976', '0'),    # Mongolie
    'ME': ('382', '0'),    # Monténégro
    'MA': ('212', '0'),    # Maroc
    'MZ': ('258', None),   # Mozambique
    'MM': ('95', '0'),     # Myanmar
    'NA': ('264', '0'),    # Namibie
    'NR': ('674', None),   # Nauru
    'NP': ('977', '0'),    # Népal
    'NL': ('31', '0'),     # Pays-Bas
    'NZ': ('64', '0'),     # Nouvelle-Zélande
    'NI': ('505', None),   # Nicaragua
    'NE': ('227', None),   # Niger
    'NG': ('234', '0'),    # Nigeria
    'NO': ('47', None),    # Norvège
    'OM': ('968', None),   # Oman
    'PK': ('92', '0'),     # Pakistan
    'PW': ('680', None),   # Palaos
    'PS': ('970', '0'),    # Palestine
    'PA': ('507', None),   # Panama
    'PG': ('675', None),   # Papouasie-Nouvelle-Guinée
    'PY': ('595', '0'),    # Paraguay
    'PE': ('51', '0'),     # Pérou
    'PH': ('63', '0'),     # Philippines
    'PL': ('48', None),    # Pologne
    'PT': ('351', None),   # Portugal
    'QA': ('974', None),   # Qatar
    'RO': ('40', '0'),     # Roumanie
    'RU': ('7', '8'),      # Russie
    'RW': ('250', None),   # Rwanda
    'WS': ('685', None),   # Samoa
    'SM': ('378', None),   # Saint-Marin
    'ST': ('239', None),   # Sao Tomé-et-Principe
    'SA': ('966', '0'),    # Arabie saoudite
    'SN': ('221', None),   # Sénégal
    'RS': ('381', '0'),    # Serbie
    'SC': ('248', None),   # Seychelles
    'SL': ('232', '0'),    # Sierra Leone
    'SG': ('65', None),    # Singapour
    'SK': ('421', '0'),    # Slovaquie
    'SI': ('386', '0'),    # Slovénie
    'SB': ('677', None),   # Îles Salomon
    'SO': ('252', None),   # Somalie
    'ZA': ('27', '0'),     # Afrique du Sud
    'SS': ('211', None),   # Soudan du Sud
    'ES': ('34', None),    # Espagne
    'LK': ('94', '0'),     # Sri Lanka
    'SD': ('249', '0'),    # Soudan
    'SR': ('597', None),   # Suriname
    'SZ': ('268', None),   # Eswatini
    'SE': ('46', '0'),     # Suède
    'CH': ('41', '0'),     # Suisse
    'SY': ('963', '0'),    # Syrie
    'TW': ('886', '0'),    # Taïwan
    'TJ': ('992', '8'),    # Tadjikistan
    'TZ': ('255', '0'),    # Tanzanie
    'TH': ('66', '0'),     # Thaïlande
    'TL': ('670', None),   # Timor oriental
    'TG': ('228', None),   # Togo
    'TO': ('676', None),   # Tonga
    'TT': ('1', '1'),      # Trinité-et-Tobago
    'TN': ('216', None),   # Tunisie
    'TR': ('90', '0'),     # Turquie
    'TM': ('993', '8'),    # Turkménistan
    'TV': ('688', None),   # Tuvalu
    'UG': ('256', '0'),    # Ouganda
    'UA': ('380', '0'),    # Ukraine
    'AE': ('971', '0'),    # Émirats arabes unis
    'GB': ('44', '0'),     # Royaume-Uni
    'US': ('1', '1'),      # États-Unis
    'UY': ('598', '0'),    # Uruguay
    'UZ': ('998', '0'),    # Ouzbékistan
    'VU': ('678', None),   # Vanuatu
    'VA': ('39', None),    # Vatican
    'VE': ('58', '0'),     # Venezuela
    'VN': ('84', '0'),     # Vietnam
    'YE': ('967', '0'),    # Yémen
    'ZM': ('260', '0'),    # Zambie
    'ZW': ('263', '0'),    # Zimbabwe
}
