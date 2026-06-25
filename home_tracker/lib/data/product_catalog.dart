import '../data/firestore_service.dart' show FirestoreService;

/// Встроенный справочник типовых продуктов
const Map<String, List<String>> PRODUCT_CATALOG = {
  'Мясо и птица': [
    'Курица целая', 'Куриная грудка', 'Куриное бедро', 'Куриные ножки',
    'Куриные крылья', 'Куриный фарш', 'Свинина', 'Говядина', 'Фарш (свинина/говядина)',
  ],
  'Рыба': [
    'Морской язык', 'Сёмга дикая', 'Сельдь', 'Скумбрия', 'Тилапия',
  ],
  'Молочные и яйца': [
    'Яйца', 'Молоко', 'Сыр', 'Масло сливочное', 'Масло топлёное',
  ],
  'Бакалея': [
    'Хлеб', 'Булка', 'Печенье', 'Мука', 'Гречка', 'Рис', 'Макароны',
    'Соль', 'Сахар', 'Масло подсолнечное', 'Приправа',
  ],
  'Овощи': [
    'Лук', 'Чеснок', 'Картофель', 'Морковь',
  ],
};

/// Возвращает все названия из каталога плоским списком
List<String> allCatalogNames() {
  return PRODUCT_CATALOG.values.expand((list) => list).toList();
}

/// Хранилище всех когда-либо введённых названий (не удаляется)
Future<Set<String>> loadAllProductNames() async {
  final saved = await FirestoreService.loadProductNames();
  return {...allCatalogNames(), ...saved};
}

Future<void> saveProductName(String name) async {
  if (name.isEmpty) return;
  final saved = await FirestoreService.loadProductNames();
  saved.add(name);
  await FirestoreService.saveProductNames(saved.toList());
}
