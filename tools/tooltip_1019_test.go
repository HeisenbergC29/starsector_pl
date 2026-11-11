package main

import (
  "strings"
  "testing"
)

// The vanilla code builds these UI descriptions as individual letter + word
// fragment, so a normal translation of the word alone renders "Czuzywa".
// Check the *assembled* display text, not merely the CSV line individually.
func Test1019TooltipReassembly(t *testing.T) {
  table,err:=loadTable("1019")
  if err!=nil {t.Fatal(err)}
  cls:="com/fs/starfarer/api/impl/campaign/abilities/ToggleAbilityWithCost.class"
  m:=table[cls]
  if m==nil {t.Fatal("missing ability UI class")}
  val:=func(s string) string {p,ok:=m[s];if !ok {t.Fatalf("missing translation for %q",s)};return p}
  examples:=[]struct{ text string; want string }{
    {val("C")+val("onsumes %s light ")+val("year's")+val(" worth of fuel and reduces the combat readiness ")+val("of all ships by %s of a combat deployment."),
     "Zuzywa paliwa odpowiadajacego przelotowi na dystansie %s roku swietlnego i zmniejsza gotowosc bojowa wszystkich okretow o %s kosztu wystawienia do walki."},
    {val("C")+val("onsumes %s light ")+val("years'")+val(" worth of fuel."),
     "Zuzywa paliwa odpowiadajacego przelotowi na dystansie %s lat swietlnych."},
    {val("R")+val("educes the combat readiness")+val(" of all ships, costing up to %s supplies to recover."),
     "Zmniejsza gotowosc bojowa wszystkich okretow, a przywrocenie ich gotowosci moze kosztowac do %s jednostek zaopatrzenia."},
    {val("C")+val("onsumes %s fuel and reduces the combat readiness")+val(" of all ships, costing up to %s supplies to recover."),
     "Zuzywa %s paliwa i zmniejsza gotowosc bojowa wszystkich okretow, a przywrocenie ich gotowosci moze kosztowac do %s jednostek zaopatrzenia."},
    {val(" c")+val("onsumes %s fuel."), " zuzywa %s paliwa."},
    {val(" r")+val("educes the combat readiness"), " zmniejsza gotowosc bojowa"},
  }
  for _,ex:=range examples {
    if ex.text!=ex.want {t.Errorf("assembled label incorrect:\n got %q\nwant %q",ex.text,ex.want)}
    if strings.Contains(ex.text,"Czuzywa")||strings.Contains(ex.text,"Rzmniejsza")||strings.Contains(ex.text,"years'") {t.Fatalf("English UI leftovers: %q",ex.text)}
  }
}