package CWRemote;

import java.time.ZonedDateTime;
import java.time.ZoneOffset;

// import java.io.FileInputStream;
// import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.ByteArrayInputStream;

import java.nio.file.Paths;
import java.nio.file.Files;
// import java.nio.ByteBuffer;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Pos;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.control.Slider;
import javafx.scene.control.ChoiceBox;
import javafx.stage.Stage;

import javafx.collections.FXCollections;

import javafx.scene.image.Image;
import javafx.scene.image.ImageView;

import javafx.scene.control.Button;
import javafx.scene.control.ToggleButton;
import javafx.scene.control.Label;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;

import org.json.JSONObject;
import org.json.JSONArray;

import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;

import com.amazonaws.client.builder.AwsClientBuilder;

import com.amazonaws.services.cloudwatch.AmazonCloudWatchClient;
import com.amazonaws.services.cloudwatch.AmazonCloudWatchClientBuilder;

import com.amazonaws.services.cloudwatch.model.GetMetricWidgetImageRequest;
import com.amazonaws.services.cloudwatch.model.GetMetricWidgetImageResult;

import java.util.Timer;
import java.util.TimerTask;

import java.util.Arrays;

// Create an ImageView from widget_descriptor
//    JSONObject widget_descriptor = (JSONObject) Widget_Descriptor_List.get(0);
//    // String cw_image_request_text = widget_descriptor.toString();
//    GetMetricWidgetImageRequest cw_image_request = new GetMetricWidgetImageRequest();
//    // cw_image_request.setMetricWidget(cw_image_request_text);
//    cw_image_request.setMetricWidget(widget_descriptor.toString());
//    // Fetched image to buffer
//    GetMetricWidgetImageResult cw_image = AWS_CloudWatch_Client.getMetricWidgetImage(cw_image_request);
//    // ByteBuffer cw_image_bytebuffer = cw_image.getMetricWidgetImage();
//
//    // Image image = new Image(new ByteArrayInputStream(cw_image_bytebuffer.array()));
//    // ImageView imageView = new ImageView(image);
//    // ImageView imageView = new ImageView(new Image(new ByteArrayInputStream(cw_image_bytebuffer.array())));
//    ImageView image_view =
//    new ImageView(new Image(new ByteArrayInputStream(cw_image.getMetricWidgetImage().array())));


public class Main extends Application {

    private JSONArray Widget_Descriptor_List;
    private AmazonCloudWatchClient AWS_CloudWatch_Client;

    private ImageView Image_View_0;
    private ImageView Image_View_1;

    private Label Period_Value_Label;
    private Integer Period_Offset = 24;
    private ToggleButton[] Period_Buttons = new ToggleButton[15];
    private Button Refresh_Button;
    private ToggleButton[] End_Buttons = new ToggleButton[15];
    private Integer End_Offset = 0;
    private Label End_Value_Label;

    private String Local_Time_Zone_Offset () {
        ZoneOffset offset  = ZonedDateTime.now().getOffset();
        return offset.toString();
    }

    private void Prepare_Image_View (ImageView Image_View,
                                     int Position_X, int Position_Y,
                                     int Fit_Width, int Fit_Height) {
        //Setting the position of the image
        Image_View.setX(Position_X);
        Image_View.setY(Position_Y);

        //setting the fit height and width of the image view
        Image_View.setFitWidth(Fit_Width);
        Image_View.setFitHeight(Fit_Height);

        //Setting the preserve ratio of the image view
        Image_View.setPreserveRatio(true);
    }

    private void Apply_Local_Time_Zone_To_Widgets () {
        String local_tz_offset = Local_Time_Zone_Offset().replace(":", "");
        for (int i = 0, size = Widget_Descriptor_List.length(); i < size; i++) {
            JSONObject widget_descriptor = (JSONObject) Widget_Descriptor_List.get(i);
            widget_descriptor.put("timezone", local_tz_offset);
        }
    }

    private void Apply_Period_End_To_Widgets (Integer Period_Offset, Integer End_Offset) {
        int abs_period_offset = Math.abs(Period_Offset);
        int abs_end_offset = Math.abs(End_Offset);
        for (int list_idx = 0, size = Widget_Descriptor_List.length(); list_idx < size; list_idx++) {
            JSONObject widget_descriptor = (JSONObject) Widget_Descriptor_List.get(list_idx);
            widget_descriptor.put("start", ("-PT" + String.valueOf(abs_period_offset + abs_end_offset) + "H"));
            widget_descriptor.put("end", ("-PT" + String.valueOf(abs_end_offset) + "H"));
        }
    }

    private ImageView ImageView_from_Widget_Descriptor (int Widget_Descrptor_Index) {
        Apply_Local_Time_Zone_To_Widgets();

        // Create an ImageView from widget_descriptor
        JSONObject widget_descriptor = (JSONObject) Widget_Descriptor_List.get(Widget_Descrptor_Index);
        // String cw_image_request_text = widget_descriptor.toString();
        GetMetricWidgetImageRequest cw_image_request = new GetMetricWidgetImageRequest();
        // cw_image_request.setMetricWidget(cw_image_request_text);
        cw_image_request.setMetricWidget(widget_descriptor.toString());
        // Fetched image to buffer
        GetMetricWidgetImageResult cw_image = AWS_CloudWatch_Client.getMetricWidgetImage(cw_image_request);
        // ByteBuffer cw_image_bytebuffer = cw_image.getMetricWidgetImage();

        // Image image = new Image(new ByteArrayInputStream(cw_image_bytebuffer.array()));
        // ImageView imageView = new ImageView(image);
        // ImageView imageView = new ImageView(new Image(new ByteArrayInputStream(cw_image_bytebuffer.array())));
        return new ImageView(new Image(new ByteArrayInputStream(cw_image.getMetricWidgetImage().array())));
    }

    private Image Image_from_Widget_Descriptor (int Widget_Descrptor_Index) {
        Local_Time_Zone_Offset();

        // Create an ImageView from widget_descriptor
        JSONObject widget_descriptor = (JSONObject) Widget_Descriptor_List.get(Widget_Descrptor_Index);
        // String cw_image_request_text = widget_descriptor.toString();
        GetMetricWidgetImageRequest cw_image_request = new GetMetricWidgetImageRequest();
        // cw_image_request.setMetricWidget(cw_image_request_text);
        cw_image_request.setMetricWidget(widget_descriptor.toString());
        // Fetched image to buffer
        GetMetricWidgetImageResult cw_image = AWS_CloudWatch_Client.getMetricWidgetImage(cw_image_request);
        // ByteBuffer cw_image_bytebuffer = cw_image.getMetricWidgetImage();

        // Image image = new Image(new ByteArrayInputStream(cw_image_bytebuffer.array()));
        return new Image(new ByteArrayInputStream(cw_image.getMetricWidgetImage().array()));
    }

    private void CW_Remote_Refresh () {
        Image_View_0.setImage(Image_from_Widget_Descriptor(0));
        Image_View_1.setImage(Image_from_Widget_Descriptor(1));
    }

    private void CW_Remote_Start ( int Button_Index, int Button_Value ) {
//        if (Button_Value < End_Offset) {
            Period_Value_Label.setText(String.valueOf(Button_Value) + "H period");
            Period_Offset = Button_Value;
            Apply_Period_End_To_Widgets(Period_Offset, End_Offset);
            CW_Remote_Refresh();
            for (int button_idx = 0, size = Period_Buttons.length;  button_idx < size; button_idx++) {
                Period_Buttons[button_idx].setSelected(button_idx == Button_Index);
//                int idx_button_offset = Integer.parseInt(Start_Buttons[button_idx].getText());
//                Start_Buttons[button_idx].setDisable(idx_button_offset >= End_Offset);
            }
//        }
//        else Start_Buttons[Button_Index].setSelected(false);
        Refresh_Button.requestFocus();
    }

    private void CW_Remote_End ( int Button_Index, int Button_Value ) {
//        if (Button_Value > Start_Offset) {
            End_Value_Label.setText("ending " + String.valueOf(Button_Value) + "H ago");
            End_Offset = Button_Value;
            Apply_Period_End_To_Widgets(Period_Offset, End_Offset);
            CW_Remote_Refresh();
            for (int button_idx = 0, size = End_Buttons.length; button_idx < size; button_idx++) {
                End_Buttons[button_idx].setSelected(button_idx == Button_Index);
//                int idx_button_offset = Integer.parseInt(End_Buttons[button_idx].getText());
//                End_Buttons[button_idx].setDisable(idx_button_offset <= Start_Offset);
            }
//        }
//        else End_Buttons[Button_Index].setSelected(false);
        Refresh_Button.requestFocus();
    }

    @Override
    public void start ( Stage stage ) {

        //Setting title to the Stage
        stage.setTitle("CW_Remote");

        String cw_remote_ini_json = "";
        try {
            cw_remote_ini_json = new String(Files.readAllBytes(Paths.get("./CW_Remote.ini")));
        } catch (IOException io_err) {
            io_err.printStackTrace();
        }

        JSONObject cw_remote_ini = new JSONObject(cw_remote_ini_json);

        // Deprecated
//         AWSCredentials aws_credentials = new BasicAWSCredentials("AKIAJ3GF3XWXXRLBIH2A", "MA0tWVGtNTPU1gbvEcQDfphDaSPzAZlyrz0IlsBg");
//         AmazonCloudWatchClient aws_cw_client = new AmazonCloudWatchClient(aws_credentials);
//         aws_cw_client.setEndpoint(Regions.US_EAST_1.name());

        BasicAWSCredentials aws_credentials =
            new BasicAWSCredentials("AKIAJ3GF3XWXXRLBIH2A", "MA0tWVGtNTPU1gbvEcQDfphDaSPzAZlyrz0IlsBg");
        AWS_CloudWatch_Client = (AmazonCloudWatchClient)
            AmazonCloudWatchClientBuilder.standard()
                .withCredentials(new AWSStaticCredentialsProvider(aws_credentials))
                .withEndpointConfiguration(
                    new AwsClientBuilder.EndpointConfiguration(
                        "monitoring.us-east-1.amazonaws.com","us-east-1"))
                .build();

        Widget_Descriptor_List = (JSONArray) cw_remote_ini.get("widget_descriptor_list");

        // Apply_Period_End_To_Widgets(-1, 0);

        Image_View_0 = ImageView_from_Widget_Descriptor(0);

        Prepare_Image_View (Image_View_0, 0, 0, 1280, 380);

        Image_View_1 = ImageView_from_Widget_Descriptor(1);

        Prepare_Image_View (Image_View_1, 0, 400, 1280, 380);

        Period_Value_Label = new Label("24H period");
        // Slider Start_Slider = new Slider(-24, -1, -24);
        HBox Period_Button_Box = new HBox();
        int[] period_button_values = new int[] {120, 96, 72, 48, 24, 20, 16, 12, 8, 6, 5, 4, 3, 2, 1};
        for (int button_idx = 0, size = period_button_values.length;  button_idx < size; button_idx++) {
            ToggleButton this_button =  new ToggleButton(String.valueOf(period_button_values[button_idx]));
            Period_Buttons[button_idx] = this_button;
            int idx = button_idx;
            this_button.setOnAction(click -> { CW_Remote_Start(idx, period_button_values[idx]); });
            this_button.setSelected(period_button_values[idx] == 24);
            Period_Button_Box.getChildren().add(this_button);
        }
        Refresh_Button = new Button("Refresh");
        Refresh_Button.setOnAction(click -> { CW_Remote_Refresh(); });
        Refresh_Button.requestFocus();

        HBox End_Button_Box = new HBox();
        int[] end_button_values = new int[] {-96, -72, -48, -36, -24, -12, -10, -8, -6, -5, -4, -3, -2, -1, 0};
        for (int button_idx = 0, size = end_button_values.length;  button_idx < size; button_idx++) {
            ToggleButton this_button =  new ToggleButton(String.valueOf(end_button_values[button_idx]));
            End_Buttons[button_idx] = this_button;
            int idx = button_idx;
            this_button.setOnAction(click -> { CW_Remote_End(idx, end_button_values[idx]); });
            this_button.setSelected(button_idx == (end_button_values.length - 1));
            End_Button_Box.getChildren().add(this_button);
        }
        // Slider End_Slider = new Slider(-23, 0, 0);
        End_Value_Label = new Label("ending 0H ago");

        HBox Control_Bar = new HBox(Period_Value_Label, Period_Button_Box, Refresh_Button, End_Button_Box, End_Value_Label);
        Control_Bar.setSpacing(5);
        Control_Bar.setAlignment(Pos.CENTER);

        VBox root = new VBox(Image_View_0, Control_Bar, Image_View_1);
        root.setAlignment(Pos.CENTER);
        Scene scene = new Scene(root, 1280, 800);
        stage.setScene(scene);

        stage.show();

        Refresh_Button.requestFocus();

        // Doesn't work:
        // stage.setOnCloseRequest(e -> Platform.exit());
        // Works:
        // stage.setOnCloseRequest(event -> System.exit(0));
        // Works:
        stage.setOnCloseRequest (event -> {
                Platform.exit();
                System.exit(0);
            });

        new Timer().scheduleAtFixedRate(new TimerTask() {
            public void run() {
                CW_Remote_Refresh();
            }
        }, 60000, 60000);
    }

    // /System/Library/CoreServices/Jar Launcher.app

    public static void main(String[] args) {
        launch(args);
    }
}
