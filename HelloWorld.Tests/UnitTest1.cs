using Xunit;

public class HelloWorldTests
{
    [Fact]
    public void GetMessage_ReturnsCorrectMessage()
    {
        // Arrange
        var expectedMessage = "Hello, World!";

        // Act
        var actualMessage = Program.GetMessage();

        // Assert
        Assert.Equal(expectedMessage, actualMessage);
    }
}

