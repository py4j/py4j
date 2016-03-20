package py4j;

import org.junit.Test;

import java.util.Arrays;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;

public class Base64Test {

	@Test
	public void testEncodeToByte() {
		byte[] bytes = new byte[128];
		for (int i = 0; i < 128; i++) {
			bytes[i] = (byte) i;
		}

		byte[] encoded = Base64.encodeToByte(bytes, true);
		byte[] encodedNoSep = Base64.encodeToByte(bytes, false);
		String encodedString = Base64.encodeToString(bytes, true);
		String encodedStringNoSep = Base64.encodeToString(bytes, false);
		char[] encodedChar = Base64.encodeToChar(bytes, true);
		char[] encodedCharNoSep = Base64.encodeToChar(bytes, false);
		byte[] decoded = Base64.decode(encoded);
		byte[] decodedNoSep = Base64.decode(encodedNoSep);
		byte[] fastDecoded = Base64.decodeFast(encoded);
		byte[] fastDecodedNoSep = Base64.decodeFast(encodedNoSep);
		byte[] decodedString = Base64.decode(encodedString);
		byte[] decodedStringNoSep = Base64.decode(encodedStringNoSep);
		byte[] decodedStringFast = Base64.decodeFast(encodedString);
		byte[] decodedStringFastNoSep = Base64.decodeFast(encodedStringNoSep);
		byte[] decodedChar = Base64.decode(encodedChar);
		byte[] decodedCharNoSep = Base64.decode(encodedCharNoSep);
		byte[] decodedCharFast = Base64.decodeFast(encodedChar);
		byte[] decodedCharFastNoSep = Base64.decodeFast(encodedCharNoSep);

		assertFalse(Arrays.equals(encoded, encodedNoSep));
		assertEquals(bytes.length, decoded.length);
		assertEquals(bytes.length, decodedNoSep.length);
		assertArrayEquals(bytes, decoded);
		assertArrayEquals(bytes, decodedNoSep);
		assertArrayEquals(bytes, fastDecoded);
		assertArrayEquals(bytes, fastDecodedNoSep);
		assertArrayEquals(bytes, decodedString);
		assertArrayEquals(bytes, decodedStringNoSep);
		assertArrayEquals(bytes, decodedStringFast);
		assertArrayEquals(bytes, decodedStringFastNoSep);
		assertArrayEquals(bytes, decodedChar);
		assertArrayEquals(bytes, decodedCharNoSep);
		assertArrayEquals(bytes, decodedCharFast);
		assertArrayEquals(bytes, decodedCharFastNoSep);

	}
}
