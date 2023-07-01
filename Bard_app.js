import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends AppCompatActivity {

    // WebView instance to display the webpage
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Create a WebView object
        webView = new WebView(this);

        // Configure the WebView settings
        webView.getSettings().setJavaScriptEnabled(true);
        webView.setWebViewClient(new WebViewClient());

        // Load the URL in the WebView
        webView.loadUrl("https://bard.google.com");

        // Set the WebView as the activity's content view
        setContentView(webView);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            // If WebView can go back, navigate back
            webView.goBack();
        } else {
            // If WebView cannot go back, finish the activity
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        // Remove WebView before destroying the activity to release resources
        if (webView != null) {
            webView.loadUrl("about:blank");
            webView.stopLoading();
            webView.setWebViewClient(null);
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
