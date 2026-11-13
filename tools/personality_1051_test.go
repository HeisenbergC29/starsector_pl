package main

import (
    "bytes"
    "testing"
)

func TestPersonalityTooltipOnlyTwoLdCOperands(t *testing.T) {
    oldTail := append([]byte{0x11, 0x22, 0x33}, personalityTooltipOriginal...)
    oldTail = append(oldTail, 0x44, 0x55, 0x66)
    translated, err := rewritePersonalityTooltipTail(oldTail)
    if err != nil { t.Fatal(err) }
    at := bytes.Index(translated, personalityTooltipOriginal[:4])
    if at < 0 { t.Fatal("expected unchanged prefix") }
    if translated[at+13] != 0x50 || translated[at+18] != 0x54 {
        t.Fatalf("expected only #44 -> #80 and #47 -> #84: %x", translated)
    }
    differences := 0
    for i := range oldTail {
        if translated[i] != oldTail[i] {
            differences++
            if i != at+13 && i != at+18 { t.Fatalf("unexpected JVM bytecode change at %d", i) }
        }
    }
    if differences != 2 || !bytes.Equal(oldTail[3:3+12], translated[3:3+12]) { t.Fatal("incorrect edit count or opcodes changed") }
    if bytes.Equal(oldTail, translated) { t.Fatal("no change") }
    if _, err := rewritePersonalityTooltipTail(oldTail[:5]); err == nil { t.Fatal("partial pattern accepted") }
    if _, err := rewritePersonalityTooltipTail(append(oldTail, personalityTooltipOriginal...)); err == nil { t.Fatal("duplicate method signature accepted") }
    corrupted := append([]byte(nil), oldTail...); corrupted[at+13] = 0x2d
    if _, err := rewritePersonalityTooltipTail(corrupted); err == nil { t.Fatal("unknown constant-pool reference accepted") }
}

func TestPersonalityOldMapCannotActivateException(t *testing.T) {
    original := []byte("original-not-the-real-class")
    patched := []byte("patched-not-the-real-class")
    previous, err := patchPersonalityTooltip(original, patched, map[string]string{personalityMixEnglish:"old translation"})
    if err != nil || !bytes.Equal(previous, patched) { t.Fatal("legacy mapping unexpectedly changes bytecode", err) }
    _, err = patchPersonalityTooltip(original, patched, map[string]string{personalityMixEnglish:personalityMixPolish})
    if err == nil { t.Fatal("current mapping must reject unknown source-class checksum") }
}
