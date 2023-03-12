#include <cs50.h>
#include <stdio.h>

int main(void)
{
   bool sw = false;
   long n = get_long("Number: ");
   int luhn = 0;
   int luhnd = 0;
   int totald = 0;
   string card;
   long cp = n;
   while(cp>0){
    totald = totald+1;
    cp/=10;
   }
   if(totald<13){
    printf("INVALID\n");
    return 0;
   }
   else if(totald > 16){
    printf("INVALID\n");
    return 0;
   }
   else if(totald == 14){
    printf("INVALID\n");
    return 0;
   }
   else if(totald == 16){
    cp = n;
    while(cp > 100){
        cp /= 10;
    }
    if(cp == 51 || cp == 52 || cp ==53 || cp == 54 || cp == 55){
        card = "MASTERCARD\n";
    }
    else if(cp/10 == 4){
        card = "VISA\n";
    }
    else{
        printf("INVALID\n");
        return 0;
    }
   }
   else if(totald == 13){
    cp = n;
    while(cp > 10){
        cp/=10;
    }
    if(cp==4){
        card = "VISA\n";
    }
    else {
        printf("INVALID\n");
        return 0;
    }
   }
   else if(totald == 15){
    cp = n;
    while(cp > 100){
        cp/=10;
    }
    if(cp == 34 || cp == 37){
        card = "AMEX\n";
    }
    else{
        printf("INVALID\n");
        return 0;
    }
   }
   else{
    printf("INVALID\n");
    return 0;
   }
   while(n > 0){
    if(sw){
        int x = 2*(n%10);
        while(x>0){
            luhnd+=(x%10);
            x/=10;
        }
        sw = false;
    }
    else{
        int x = (n%10);
        while(x>0){
            luhn += (x%10);
            x/=10;
        }
        sw = true;
    }
    n/=10;
   }
   if((luhnd+luhn)%10 == 0){
    printf("%s", card);
   }
   else{
    printf("luhn %i\n", luhnd + luhn);
    printf("INVALID\n");
   }
}