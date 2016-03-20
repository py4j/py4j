/******************************************************************************
 * Copyright (c) 2009-2016, Barthelemy Dagenais and individual contributors.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *****************************************************************************/
package py4j;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;

import java.util.Arrays;

import org.junit.Test;

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
