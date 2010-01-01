package py4j.reflection;

public class TypeConverter {

	public final static int NO_CONVERSION = -1;
	public final static int DOUBLE_TO_FLOAT = 0;
	public final static int INT_TO_SHORT = 1;
	public final static int INT_TO_BYTE = 2;
	public final static int STRING_TO_CHAR = 3;

	private final int conversion;

	public final static TypeConverter NO_CONVERTER = new TypeConverter();
	public final static TypeConverter FLOAT_CONVERTER = new TypeConverter(DOUBLE_TO_FLOAT);
	public final static TypeConverter SHORT_CONVERTER = new TypeConverter(INT_TO_SHORT);
	public final static TypeConverter BYTE_CONVERTER = new TypeConverter(INT_TO_BYTE);
	public final static TypeConverter CHAR_CONVERTER = new TypeConverter(STRING_TO_CHAR);
	
	public TypeConverter() {
		this(NO_CONVERSION);
	}
	
	public TypeConverter(int conversion) {
		this.conversion = conversion;
	}

	public Object convert(Object obj) {
		Object newObject = null;

		switch (conversion) {
		case NO_CONVERSION:
			newObject = obj;
			break;
		case DOUBLE_TO_FLOAT:
			newObject = ((Double) obj).floatValue();
			break;
		case INT_TO_SHORT:
			newObject = ((Integer) obj).shortValue();
			break;
		case INT_TO_BYTE:
			newObject = ((Integer) obj).byteValue();
			break;
		case STRING_TO_CHAR:
			newObject = ((CharSequence) obj).charAt(0);
			break;
		}

		return newObject;
	}

}
